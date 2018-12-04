from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError


class ProductCategory(models.Model):
    _inherit = "product.category"

    attributes_ids = fields.Many2many('product.custom.attribute', string='Attributes', required=True)


    @api.model
    def create(self, vals):

        x = super(ProductCategory, self).create(vals)
        return x
    @api.multi
    def write(self, vals):
        y = super(ProductCategory, self).write(vals)
        pr_tmp = self.env['product.template']
        p_att_line = self.env['product.attribute.lines']
        prd_li = pr_tmp.search([('categ_id','=',self.id)])
        for i in prd_li:
            for m in i.product_custom_attribute_ids:
                print("this is modified",m.is_modified)
                if not m.is_modified:
                    t=0
                    for j in self.attributes_ids:
                        if m.attribute_id == j.id:
                            t=1
                            break;
                    if t==0:
                        m.unlink()
            a_lines = p_att_line.search([('product_template_id','=',i.id)])
            if len(a_lines) == 0:
                for j in self.attributes_ids:
                    a_lines.create({
                    'product_template_id':i.id,
                    'attribute_id':j.id
                    })

            else:
                for l in self.attributes_ids:
                    t=0
                    for k in a_lines:
                        print("_______________ ",k.attribute_id.id,l.id)
                        if k.attribute_id.id == l.id:
                            t=1
                            print("inside+++++")

                    if t==0:
                        a_lines.create({
                        'product_template_id':i.id,
                        'attribute_id':l.id
                        })



        return y

    # @api.onchange('attributes_ids')
    # def attr_fx(self):
    #     print(self.attributes_ids)
    #     pr_tmp = self.env['product.template']
    #     p_att_line = self.env['product.attribute.lines']
    #     record = pr_tmp.search([])
    #     for i in record:
    #         # print('rec:::::::::::::::>',i)
    #         # rec= i.product_custom_attribute_ids.attribute_id
    #
    #         rec = pr_al.search([('product_template_id','=',i.id)])
    #         if len(rec) == 0:
    #             for j in self.attributes_ids:
    #                 pr_al.create({
    #                 'product_template_id':i.id,
    #                 'attribute_id':j.id
    #                 })
    #
    #         else:
    #             for l in self.attributes_ids:
    #                 t=0
    #                 for k in rec:
    #                     print("_______________ ",k.attribute_id,l.id)
    #                     if k.search([('attribute_id','=',l.id)]):
    #                         t=1
    #                         print("inside+++++")
    #
    #                 if t==0:
    #                     pr_al.create({
    #                     'product_template_id':i.id,
    #                     'attribute_id':l.id
    #                     })







            # print("?????????",rec)
            # for k in rec:
            #     for j in self.attributes_ids:
            #         rec2 = k.search([('attribute_id','=',j.id)])
            #         print("???????????",len(rec))
            # for j in self.attributes_ids:
            #
            #     for k in rec:
            #         if k.search([('attribute_id','=',j.id)]):
            #             t=1
            #             print("++++++",t)
            #
            #
            #     print("///////////////////")
            #     if t == 0:
            #         self.env['product.attribute.lines'].create({
            #             'product_template_id':i.id,
            #             'attribute_id':j.id
            #         })
            #

            # for j in self.attributes_ids:
            #     i.product_custom_attribute_ids.attribute_id=j.id
            #     print(j)
            #     # i.write({
            #     # 'barcode':'abc'
            #     # })

class ValuesLine(models.Model):
    _name = 'values.line'

    name = fields.Char('Values')
    value_id = fields.Many2one('product.custom.attribute', 'Value')


class ProductCustomAttribute(models.Model):
    _name = 'product.custom.attribute'
    _description = 'Product Attribute'

    name = fields.Char('Attribute Name')
    value_type = fields.Selection([
				    ('char', 'Char'),
				    ('integer', 'Integer'),
				    ('float', 'Float'),
				    ('text', 'Text'),
				    ('date', 'Date'),
                    ('datetime', 'Datetime'),
                    ('selection', 'Selection'),
                    ('multiple_select', 'Multiple Select'),
				], string='Value Type')
    values_ids = fields.One2many('values.line', 'value_id', 'Values')


    @api.multi
    def write(self, vals):
        if not vals['value_type']:
            raise ValidationError(_('You are not allowed to change the Value Type since the field has laready been created!'))



    @api.model
    def create(self, vals):
        return super(ProductCustomAttribute, self).create(vals)
        product_id = self.env['ir.model'].search([('model', '=', 'product.template')], limit=1)
        selection_options = {}
        if 'values_ids' in vals and vals['values_ids']:
            for case in vals['values_ids']:
                pa_line = case[2]['name']
                selection_options[str(pa_line).lower()] = str(pa_line)
        self.env['ir.model.fields'].sudo().create({'name': "x_" + vals['name'],
                                                    'field_description': vals['name'],
                                                    'model_id': product_id.id,
                                                    'ttype': vals['value_type'] if vals['value_type'] != 'multiple_select' else 'selection',
                                                    'selection': str(selection_options.items()),
                                                    'active': True
                                                    })
        inherit_id = self.env.ref('product_attribute.view_product_template_inherit')
        arch_base = _('<?xml version="1.0"?>'
                      '<data>'
                        '<field name="product_custom_attribute_ids" position="after">'
                        '<group colspan="2" col="2">'
                        '<field name="%s"/>'
                        '</group>'
                        '</field>'
                      '</data>') % ("x_" + vals['name'])
        self.env['ir.ui.view'].sudo().create({'name': 'product.template.fields',
                                              'type': 'form',
                                              'model': 'product.template',
                                              'mode': 'extension',
                                              'inherit_id': inherit_id.id,
                                              'arch_base': arch_base,
                                              'active': True})
        return super(ProductCustomAttribute, self).create(vals)



class ProductAttributeLines(models.Model):
    _name = "product.attribute.lines"

    attribute_id = fields.Many2one('product.custom.attribute', string='Attribute')
    value_type  = fields.Selection(related='attribute_id.value_type')
    char_val = fields.Char(string="Char")
    integer_val = fields.Integer(string="Integer")
    float_val = fields.Float(string="Float")
    text_val = fields.Text(string="Text")
    date_val = fields.Date(string="Date")
    datetime_val = fields.Datetime(string="Datetime")
    selection_id = fields.Many2one('values.line', string="Selection")
    values_ids = fields.Many2many('values.line', string="Multiple Select")
    product_template_id = fields.Many2one('product.template', 'Product Template')
    is_modified = fields.Boolean(string="Value Updated" )




    @api.model
    def create(self, vals):
        res = super(ProductAttributeLines, self).create(vals)
        print("create  callling_lines",vals,res)
        # pro_cats = self.env['product.category']
        # pr_tmp = self.env['product.template']
        # if not vals['is_modified']:
        #     res.unlink()
        #     res.id=0
        #     print("ya===========333")
            # prd_li = pr_tmp.search([('id','=',vals['product_template_id'])])
            # cat_li = pro_cats.search([('id','=',prd_li.categ_id.id)])
            # t=0
            # for atrrs in cat_li.attributes_ids:
            #     if atrrs.id == self.id:
            #         t=1
            #         break
            # if t == 0:
                
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductAttributeLines, self).write(vals)
        pro_cats = self.env['product.category']
        pr_tmp = self.env['product.template']

        if 'is_modified' in vals:
            if not vals['is_modified']:
                prd_li = pr_tmp.search([('id','=',self.product_template_id.id)])
                cat_li = pro_cats.search([('id','=',prd_li.categ_id.id)])
                t=0
                for atrrs in cat_li.attributes_ids:
                    if atrrs.id == self.attribute_id.id:
                        t=1
                        break
                if t == 0:
                    self.unlink()
        #     x = super(ProductAttributeLines, self).write({'is_modified':True})
        print("write callling")
        return res


    @api.onchange('integer_val','char_val','float_val','text_val')
    def modify_line(self):
        if self.integer_val or self.char_val:
            self.is_modified = True
        else:
            self.is_modified = False
            
            









class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_custom_attribute_ids = fields.One2many('product.attribute.lines', 'product_template_id', 'Attributes')


    @api.onchange('categ_id')
    def cat_change(self):
        print("categ_change=======",self.categ_id)
        pro_cats = self.env['product.category']
        print("create vals..",self.categ_id.attributes_ids)
        p_att_line = self.env['product.attribute.lines']
        a_lines = p_att_line.search([('product_template_id','=',self.id)])
        print("llllllll..........",p_att_line)
        procat = []
        for m in self.product_custom_attribute_ids:
            print("this is m====",m)
            if m.is_modified:
                procat.append([0,0,{'product_template_id':self.id,'attribute_id':m.attribute_id,'is_modified':m.is_modified,'char_val':m.char_val,'integer_val':m.integer_val}])

        for l in self.categ_id.attributes_ids:
            t=0
            for m in self.product_custom_attribute_ids:
                if m.attribute_id.id == l.id and m.is_modified:
                    t=1
                    break
            if t == 0:
                procat.append([0,0,{'product_template_id':self.id,'attribute_id':l.id}])
            
        return {'value':{'product_custom_attribute_ids':procat}}


    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)

        pro_cats = self.env['product.category']
        p_att_line = self.env['product.attribute.lines']
        for l in self.categ_id.attributes_ids:
            p_att_line.create({
            'product_template_id':self.id,
            'attribute_id':l.id,

            })



        # a_lines = p_att_line.search([('product_template_id','=',self.id)])
        # if len(a_lines) == 0:
        #     for j in self.categ_id.attributes_ids:
        #         a_lines.create({
        #         'product_template_id':self.id,
        #         'attribute_id':j.id
        #         })
        # else:


        # categ = pro_cats.search([('id','=',self.categ_id)])

        # print("ctegry is",categ)
        # field_name = vals.keys()[0][2:]
        # product_attr_id = self.env['product.custom.attribute'].search([('name','=',field_name)])
        # self.product_custom_attribute_ids.update({
        #         'attribute_id': product_attr_id,
        #         'char_val' : vals[vals.keys()[0]] if vals.keys()[0] or vals.keys()[0] == 'product_custom_attribute_ids' else False
        #     })
        return res


    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        print("write_______template")

        if 'product_custom_attribute_ids' in vals:
            print("line crea/dele",vals)

        # if 'categ_id' in vals:
        #     print("inside categ change")
        #     pro_cats = self.env['product.category']

        #     for m in self.product_custom_attribute_ids:
        #         print("this is modified",m.is_modified)
        #         if not m.is_modified:
        #             t=0
        #             for j in self.categ_id.attributes_ids:
        #                 if m.attribute_id == j.id:
        #                     t=1
        #                     break
        #             if t==0:
        #                 m.unlink()
        #     p_att_line = self.env['product.attribute.lines']
        #     a_lines = p_att_line.search([('product_template_id','=',self.id)])
        #     if len(a_lines) == 0:
        #         for j in self.categ_id.attributes_ids:
        #             a_lines.create({
        #             'product_template_id':self.id,
        #             'attribute_id':j.id
        #             })
        #     else:
        #         for l in self.categ_id.attributes_ids:
        #             t=0
        #             for k in a_lines:
        #                 print("_______________ ",k.attribute_id.id,l.id)
        #                 if k.attribute_id.id == l.id:
        #                     t=1
        #                     print("inside+++++")

        #             if t==0:
        #                 a_lines.create({
        #                 'product_template_id':self.id,
        #                 'attribute_id':l.id
        #                 })



        # categ = pro_cats.search([('id','=',self.categ_id)])

        # print("ctegry is",categ)
        # field_name = vals.keys()[0][2:]
        # product_attr_id = self.env['product.custom.attribute'].search([('name','=',field_name)])
        # self.product_custom_attribute_ids.update({
        #         'attribute_id': product_attr_id,
        #         'char_val' : vals[vals.keys()[0]] if vals.keys()[0] or vals.keys()[0] == 'product_custom_attribute_ids' else False
        #     })
        return res
