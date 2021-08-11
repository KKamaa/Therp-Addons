# -*- coding: utf-8 -*-
# Copyright 2015-2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
import threading

from email.utils import COMMASPACE

from odoo import _, api, models
from odoo.addons.base.ir.ir_mail_server import extract_rfc2822_addresses


_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    # pylint: disable=too-few-public-methods
    _inherit = 'ir.mail_server'

    @api.model
    def patch_message(self, message):
        """Override message recipients.

        Result is dependent on what is specified in the configuration:
        1. Message is not changed (no configuration or 'disabled');
        2. Message recipients are replaced;
        3. There is no valid recipient in the override configuration.

        If there is no valid recipient, an Exception will be thrown. This
        will be an AssertionException, in line with what is done by standard
        Odoo. Most likely this message will be catched and an appropiate
        reason for non delivery registered.
        """
        config_model = self.env['ir.config_parameter']
        override_email = config_model.get_param(
            'override_mail_recipients.override_to', default='disable')
        if override_email == 'disable':
            return
        actual_recipients = extract_rfc2822_addresses(override_email)
        if not actual_recipients:
            # In test of other modules we should not cause an assert
            # Exception, but in test of this module, we should.
            test_mode = getattr(threading.currentThread(), 'testing', False)
            in_other_test = test_mode and \
                not self.env.context.get('test_override_mail', False)
            if in_other_test:
                _logger.info(
                    _("No valid override_email_to during testing in %s"),
                    override_email)
                return  # Practically disable for other tests.
            # Throw assertion error, to make sure send failure logged with
            # message.
            assert actual_recipients, 'No valid override_email_to'
        # If we get here, we have a valid override
        for field in ['to', 'cc', 'bcc']:
            if not message[field]:
                continue
            original = COMMASPACE.join(message.get_all(field, []))
            not_so_original = original.replace('\\', '').replace(
                '"', '\\"').replace('<', '[').replace('>', ']').replace(
                    '@', '(at)')
            del message[field]
            message[field] = COMMASPACE.join(
                '"%s" <%s>' % (not_so_original, email)
                for email in actual_recipients)

    @api.model
    def send_email(
            self, message, mail_server_id=None, smtp_server=None,
            smtp_port=None, smtp_user=None, smtp_password=None,
            smtp_encryption=None, smtp_debug=False):
        """Override email recipients if requested, then send mail.

        Or throw Exception when no valid recipients.
        """
        # pylint: disable=too-many-arguments
        self.patch_message(message)
        return super(IrMailServer, self).send_email(
            message, mail_server_id=mail_server_id,
            smtp_server=smtp_server, smtp_port=smtp_port, smtp_user=smtp_user,
            smtp_password=smtp_password, smtp_encryption=smtp_encryption,
            smtp_debug=smtp_debug)
