from decimal import Decimal
from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from livesettings import config_get_group, config_value 
from payment.config import gateway_live
from payment.utils import get_processor_by_key
from payment.views import payship
from satchmo_store.shop.models import Cart
from satchmo_store.shop.models import Order, OrderPayment, Config
from satchmo_utils.dynamic import lookup_url, lookup_template
from sys import exc_info
from traceback import format_exception
from django.utils.translation import activate
import logging

import traceback

from subprocess import Popen, PIPE

log = logging.getLogger()
payment_logger = logging.getLogger('payment_logger')
payment_logger.setLevel(logging.DEBUG)

def pay_ship_info(request):
    return payship.base_pay_ship_info(request,
        config_get_group('PAYMENT_PAYBOX'), payship.simple_pay_ship_process_form,
        'shop/checkout/paybox/pay_ship.html')
pay_ship_info = never_cache(pay_ship_info)

PBX_DEVISES_ISO_4217 = {
               'EUR': 978,
               'USD': 840,
               'GBP': 826
}
def confirm_info(request):
    shop = Config.objects.get_current()

    payment_module = config_get_group('PAYMENT_PAYBOX')

    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return HttpResponseRedirect(url)
                
    log.debug(order)

    tempCart = Cart.objects.from_request(request)
    if tempCart.numItems == 0:
        template = lookup_template(payment_module, 'shop/checkout/empty_cart.html')
        return render_to_response(template, RequestContext(request))

    # Check if the order is still valid
    if not order.validate(request):
        context = RequestContext(request,
            {'message': _('Your order is no longer valid.')})
        return render_to_response('shop/404.html', context_instance=context)

    template = lookup_template(payment_module, 'shop/checkout/paybox/confirm.html')
    if payment_module.LIVE.value:
        log.debug("live order on %s", payment_module.KEY.value)
        url = payment_module.POST_URL.value
        account = payment_module.ID.value
        bksite =  payment_module.SITE.value
        rank = payment_module.RANK.value
    else:
        url = payment_module.POST_TEST_URL.value
        account = payment_module.ID_TEST.value
        bksite =  payment_module.SITE_TEST.value
        rank = payment_module.RANK_TEST.value

    try:
        address = lookup_url(payment_module,
            payment_module.RETURN_ADDRESS.value, include_server=True)
    except urlresolvers.NoReverseMatch:
        address = payment_module.RETURN_ADDRESS.value
    
    processor_module = payment_module.MODULE.load_module('processor')
    processor = processor_module.PaymentProcessor(payment_module)
    processor.create_pending_payment(order=order)
    
    # Tax
    default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX') 

    amount=order.balance
    # use external sw for creation of the form (and notification of payment on paybox platform)
    log.debug("To be payed : %s", amount)
# ./modulev3.cgi PBX_MODE=4 PBX_SITE=1999888         
    binprog = payment_module.BIN_PROG_FULLPATH.value
    args=[binprog,]
    args.append('PBX_MODE=4')
    args.append('PBX_SITE=%s'%bksite)
    args.append('PBX_RANG=%s'%rank)
    args.append('PBX_IDENTIFIANT=%s'%account)
    args.append('PBX_TOTAL=%d'%(int(amount*100)))
    args.append('PBX_CMD=%s'%order.id)
    args.append('PBX_PORTEUR=%s'%order.contact.email)
    args.append('PBX_DEVISE=%s'%PBX_DEVISES_ISO_4217['EUR'])
    
    if request.LANGUAGE_CODE=='fr':
        pbx_country_code='FRA'
    elif request.LANGUAGE_CODE=='es':
        pbx_country_code='ESP'
    elif request.LANGUAGE_CODE=='it':
        pbx_country_code='ITA'
    elif request.LANGUAGE_CODE=='de':
        pbx_country_code='DEU'
    elif request.LANGUAGE_CODE=='nl':
        pbx_country_code='NLD'
    else:
        pbx_country_code='GBR'

    args.append('PBX_LANGUE=%s'%pbx_country_code)

    args.append('PBX_RETOUR=amount:M;ref:R;autho:A;trans:T;type:P;card:C;idtrans:S;country:Y;error:E;valid:D;IP:I;BIN6:N;last2:J;tstmp:W;dgst:H;sign:K')
    args.append('PBX_OUTPUT=C')

    returl = lookup_url(payment_module,payment_module.RETURN_ADDRESS.value)
    args.append('PBX_EFFECTUE=%s%s'%(shop.base_url,returl))

    returl = lookup_url(payment_module,payment_module.FAILURE_ADDRESS.value)
    args.append('PBX_REFUSE=%s%s'%(shop.base_url,returl))

    returl = lookup_url(payment_module,payment_module.CANCELLED_ADDRESS.value)
    args.append('PBX_ANNULE=%s%s'%(shop.base_url,returl))

    # Url directly called by paybox servers : in test mode, need to be specified
    if not payment_module.LIVE.value:
        http_callback_url = lookup_url(payment_module,'PAYBOX_satchmo_checkout-cb')
        args.append('PBX_REPONDRE_A=%s%s'%(shop.base_url,http_callback_url))

    if not payment_module.LIVE.value:
        args.append('PBX_PAYBOX=%s' % url)
        args.append('PBX_BACKUP1=%s' % url)
        args.append('PBX_BACKUP2=%s' % url)
        
    log.debug("Arguments : %s ", str(args))

    # Finish form
    footer_start = "<br /><div class='wide acenter'><input style='font-size:10px;' type='SUBMIT' value='"
    footer_end =  "' /></div> </FORM>"
    value = _('Pay')
    footer = '%s%s%s'%(footer_start,value,footer_end)
#    footer= "<br /><INPUT CLASS='button' style='height:22px;font-size:10px;' TYPE='SUBMIT' VALUE='Payer' /> </FORM>"
    formstr = mark_safe("%s %s" % (Popen(args, stdout=PIPE).communicate()[0], footer ) )


    log.debug("form proposed by bin : %s", str(formstr))

    # No support for subscription. 
    
    ctx = RequestContext(
        request, 
        {'order': order,
         'default_view_tax': default_view_tax, 
         'post_url': url,
         'account': account,
         'site' : bksite,
         'rank' : rank,                              
         'currency_code': 'EUR',
         'return_address': address,
         'invoice': order.id,
         'PAYMENT_LIVE' : gateway_live(payment_module),
         'formstr':formstr
         })
    return render_to_response(template, context_instance=ctx)
confirm_info = never_cache(confirm_info)

def cb(request):
    """ Callback view """ 
    payment_module = config_get_group('PAYMENT_PAYBOX')
    # First thing : log infos given by callback
    payment_logger.info('Paybox (%s) %s %s'%(request.META['REMOTE_ADDR'], request.META['HTTP_HOST'], request.META['REQUEST_URI'] ))

    # Check ip source addr is correct
    if not request.META['REMOTE_ADDR'] in payment_module.PAYBOX_IP_ADDR.value:
        log.info('Bad source ip for cb')
        payment_logger.info('%s is not an authorized address !', request.META['REMOTE_ADDR'])
        return HttpResponse(status=403) 


    data = request.GET
    # TODO : verifier la signature du message

    if not 'error' in data:
        # no return code, cancel ! 
        log.info("Ignoring cb data for non-completed payment.")
        payment_logger.info("no error code")
        return HttpResponse(status=404) 

    if not data['error'] == '00000':
        log.warn('Unsuccesful payment, error %s'%data['error'])
        payment_logger.warn('Unsuccesful payment, error %s'%data['error'])
        return HttpResponse(status=200)

    if not 'autho' in data:
        # We want to respond to anything that isn't a payment - but we won't insert into our database.
        log.info("Ignoring cb data for non-completed payment.")
        payment_logger.info("no authorization number")
        return HttpResponse(status=404)

    live=payment_module.LIVE.value
    if data['autho'] == "XXXXXX" and live:
        # live autho show wrong autho number ...
        log.error('Wrong autho number in live mode') 
        payment_logger.error('Wrong autho number in live mode. What is going on ?') 
        return HttpResponse(status=404)
    
    if data['autho'] == "XXXXXX":
        log.debug('Autho is XXXXXX, but we are in test mode')

    try:          
        orderid=data['ref']
        txn_id=data['idtrans']
        amount=int(data['amount'])/Decimal(100)

        log.info("ref %s idtrans %s", orderid, txn_id)
        if not OrderPayment.objects.filter(transaction_id=txn_id).count():
            # If the payment hasn't already been processed:
            order = Order.objects.get(pk=orderid)
            try:
                # set lang back
                activate(order.additionalorderinformation.lang)
            except:
                log.exception("Error while setting back language")
            order.add_status(status='New', notes="%s"%data['autho'])
            processor = get_processor_by_key('PAYMENT_PAYBOX')
            payment = processor.record_payment(order=order, amount=amount, transaction_id=txn_id)
           
            for cart in Cart.objects.filter(customer=order.contact):
                cart.empty()
        else:
            log.info("Payment alredy processed")
               
    except:
        traceback.print_exc()

        log.exception(''.join(format_exception(*exc_info())))
        payment_logger.error( 'Exception during cb handler ! ')
        payment_logger.exception(''.join(format_exception(*exc_info())))

    return HttpResponse()
