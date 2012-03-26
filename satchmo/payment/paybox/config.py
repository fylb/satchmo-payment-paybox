from livesettings import *
from django.utils.translation import ugettext_lazy as _
import os
from django.conf import settings

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_PAYBOX', 
    _('Paybox Payment Module Settings'), 
    ordering = 101)

config_register_list(

StringValue(PAYMENT_GROUP,
    'CURRENCY_CODE',
    description=_('Currency Code'),
    help_text=_('Currency code for Paybox transactions.'),
    default = 'EUR'),
    
StringValue(PAYMENT_GROUP,
    'POST_URL',
    description=_('Post URL'),
    help_text=_('The Paybox URL for real transaction posting.'),
    default="https://tpeweb.paybox.com/cgi/MYchoix_pagepaiement.cgi"),

StringValue(PAYMENT_GROUP,
    'POST_TEST_URL',
    description=_('Post URL'),
    help_text=_('The Paybox URL for test transaction posting.'),
    default="https://preprod-tpeweb.paybox.com/cgi/MYchoix_pagepaiement.cgi"),

StringValue(PAYMENT_GROUP,
    'ID',
    description=_('Paybox ID'),
    help_text=_('The ID of your paybox account'),
    default=""),

StringValue(PAYMENT_GROUP,
    'ID_TEST',
    description=_('Paybox test ID'),
    help_text=_('The ID for testing your paybox account'),
    default="2"),

StringValue(PAYMENT_GROUP,
    'SITE',
    description=_('Site number (related to your bank account)'),
    help_text=_('The site number given by your bank'),
    default=""),

StringValue(PAYMENT_GROUP,
    'SITE_TEST',
    description=_('Test Site number'),
    help_text=_('Test site number given by paybox'),
    default=""),

StringValue(PAYMENT_GROUP,
    'RANK',
    description=_('Rank number (related to your bank account)'),
    help_text=_('The rank number given by your bank'),
    default=""),

StringValue(PAYMENT_GROUP,
    'RANK_TEST',
    description=_('Test Rank number'),
    help_text=_('Test Rank number given by paybox'),
    default="99"),

StringValue(PAYMENT_GROUP,
    'RETURN_ADDRESS',
    description=_('Return URL'),
    help_text=_('Where Paybox will return the customer after the purchase is complete.  This can be a named url and defaults to the standard checkout success.'),
    default="satchmo_checkout-success"),

StringValue(PAYMENT_GROUP,
    'FAILURE_ADDRESS',
    description=_('Failure return URL'),
    help_text=_('Where Paybox will return the customer in case of payment failure'),
    default="satchmo_checkout-failure"),

StringValue(PAYMENT_GROUP,
    'CANCELLED_ADDRESS',
    description=_('Return URL'),
    help_text=_('Where Paybox will return the customer in case of payment cancellation'),
    default="satchmo_checkout-cancelled"),
    
BooleanValue(PAYMENT_GROUP, 
    'LIVE', 
    description=_("Accept real payments"),
    help_text=_("False if you want to be in test mode"),
    default=False),
    
ModuleValue(PAYMENT_GROUP,
    'MODULE',
    description=_('Implementation module'),
    hidden=True,
    default = 'satchmo.payment.paybox'),

BooleanValue(PAYMENT_GROUP,
    'DEFAULT',
    description=_("Select by default"),
    help_text=_("Select this payment module by default"),
    default=False),
    
StringValue(PAYMENT_GROUP,
    'KEY',
    description=_("Module key"),
    hidden=True,
    default = 'PAYBOX'),

StringValue(PAYMENT_GROUP,
    'LABEL',
    description=_('English name for this group on the checkout screens'),
    default = 'Paybox',
    help_text = _('This will be passed to the translation utility')),

StringValue(PAYMENT_GROUP,
    'URL_BASE',
    description=_('The url base used for constructing urlpatterns which will use this module'),
    default = '^paybox/'),
    
BooleanValue(PAYMENT_GROUP,
    'EXTRA_LOGGING',
    description=_("Verbose logs"),
    help_text=_("Add extensive logs during post."),
    default=False),

StringValue(PAYMENT_GROUP,
    'BIN_PROG_FULLPATH',
    description=_('Binary program full path. (modulev3 as downloaded from paybox)'),
    default = os.path.join('/usr/local','paybox','modulev3.cgi'),),

MultipleStringValue(PAYMENT_GROUP,
    'PAYBOX_IP_ADDR',
    description=_('Paybox ip address'),
    default = [ '195.101.99.76', '194.2.122.158' ], ) , 
)

# PAYMENT_GROUP['TEMPLATE_OVERRIDES'] = {
#     'shop/checkout/confirm.html' : 'shop/checkout/paybox/confirm.html',
# }
