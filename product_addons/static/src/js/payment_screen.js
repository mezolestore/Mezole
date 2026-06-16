/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { _t } from "@web/core/l10n/translation";

patch(PosOrder.prototype, {
    setup(vals) {
        super.setup(...arguments);
        this.to_invoice = true;
        console.log("PosOrder - setup, to_invoice set to true");
    },
});

patch(PaymentScreen.prototype, {

    async validateOrder(isForceValidate) {
        const order = this.currentOrder;

        if (!order.get_partner()) {
            this.dialog.add(AlertDialog, {
                title: "Customer Required",
                body: "Please select a customer before validating the order.",
            });
            return;
        }
        let prod_used_qty = {};
        let call_super = true;
        for (const line of order.lines) {
            let prd = line.product_id;
            if (prd.type == 'consu'){
                if (prod_used_qty[prd.id]) {
                    prod_used_qty[prd.id].used_qty += line.qty;
                } else {
                    prod_used_qty[prd.id] = {
                        product: prd,
                        available_qty: prd.qty_available || 0,
                        used_qty: line.qty,
                    };
                }
            }
            if (prd.type == 'consu'){
                if(prd.qty_available <= 0 && line.qty > 1){
                    restrict = true;
                    call_super = false;
                    let warning = prd.display_name + ' is out of stock.';
                    this.env.services.pos.popup.add(ErrorPopup, {
                        title: _t('Zero Quantity Not allowed'),
                        body: _t(warning),
                    });
                }
            }
        };
            
            for (const [id, data] of Object.entries(prod_used_qty)) {
                const product = data.product;

                const remaining = data.available_qty - data.used_qty;

                if (remaining < 0) {
                    this.dialog.add(AlertDialog, {
                        title: _t("Deny Order"),
                        body: _t(`${product.display_name} is out of stock.`),
                    });
                    return;
                }
            }

        await super.validateOrder(...arguments);
    },
});

patch(PosOrderline.prototype, {

    getDisplayData() {
        return {
            ...super.getDisplayData(...arguments),
            category: this.product_id.categ_id.name,
        };
    },

    // EXTENDS 'point_of_sale'
    prepareBaseLineForTaxesComputationExtraValues(customValues = {}) {
        const extraValues = super.prepareBaseLineForTaxesComputationExtraValues(customValues);
        extraValues.category = this.product_id.categ_id.name;
        return extraValues;
    },
    
});

patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                category: { type: String, optional: true },
            },
        },
    },
});