# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import api, fields, models, _


class AccountFiscalYear(models.Model):
    _name = 'account.fiscal.year'
    _description = 'Fiscal Annee'

    name = fields.Char(string='Name', required=True)
    date_from = fields.Date(string='Date de début', required=True,)
    date_to = fields.Date(string='Date de fin', required=True,)
    company_id = fields.Many2one('res.company', string='Compagnie', required=True,
        default=lambda self: self.env.company)

    @api.constrains('date_from', 'date_to', 'company_id')
    def _check_dates(self):
        '''
        Check interleaving between fiscal years.
        There are 3 cases to consider:

        s1   s2   e1   e2
        (    [----)----]

        s2   s1   e2   e1
        [----(----]    )

        s1   s2   e2   e1
        (    [----]    )
        '''
        for fy in self:
            # La date de début doit être antérieure à la date de fin
            date_from = fy.date_from
            date_to = fy.date_to
            if date_to < date_from:
                raise ValidationError(_('La date de fin ne doit pas être antérieure à la date de début.'))


            domain = [
                ('id', '!=', fy.id),
                ('company_id', '=', fy.company_id.id),
                '|', '|',
                '&', ('date_from', '<=', fy.date_from), ('date_to', '>=', fy.date_from),
                '&', ('date_from', '<=', fy.date_to), ('date_to', '>=', fy.date_to),
                '&', ('date_from', '<=', fy.date_from), ('date_to', '>=', fy.date_to),
            ]

            if self.search_count(domain) > 0:
                raise ValidationError(_('Vous ne pouvez pas avoir de chevauchement entre deux exercices fiscaux, veuillez corriger les dates de début et/ou de fin de vos exercices.'))
