/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

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