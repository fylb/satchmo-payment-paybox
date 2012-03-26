from django.conf.urls.defaults import patterns
from satchmo_store.shop.satchmo_settings import get_satchmo_setting

ssl = get_satchmo_setting('SSL', default_value=False)

urlpatterns = patterns('',
     (r'^$', 'satchmo.payment.paybox.views.pay_ship_info', {'SSL': ssl}, 'PAYBOX_satchmo_checkout-step2'),
     (r'^confirm/$', 'site_v1.ext.satchmo.payment.paybox.views.confirm_info', {'SSL': ssl}, 'PAYBOX_satchmo_checkout-step3'),
     (r'^success/$', 'payment.views.checkout.success', {'SSL': ssl}, 'PAYBOX_satchmo_checkout-success'),

     (r'^failure/$', 'django.views.generic.simple.direct_to_template', 
      {'SSL': ssl , 'template': 'shop/checkout/failure.html'}, 
      'PAYBOX_satchmo_checkout-failure'),

     (r'^cancelled/$', 'django.views.generic.simple.direct_to_template', 
      {'SSL': ssl , 'template': 'shop/checkout/cancelled.html'}, 
      'PAYBOX_satchmo_checkout-cancelled'),


     (r'^cb/$', 'satchmo.payment.paybox.views.cb', {'SSL': ssl }, 'PAYBOX_satchmo_checkout-cb'),
     (r'^confirmorder/$', 'payment.views.confirm.confirm_free_order', 
        {'SSL' : ssl, 'key' : 'PAYBOX'}, 'PAYBOX_satchmo_checkout_free-confirm'),
)
