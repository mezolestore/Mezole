/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { actionService } from "@web/webclient/actions/action_service";

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class PasswordDialog extends Component {
    static components = { Dialog };
    static template = "mezole.PasswordDialog";

    setup() {
        this.state = useState({
            password: "",
            error: false,
        });
    }

    async confirm() {
        const expectedPassword = this.props.expectedPassword;

        if (this.state.password === expectedPassword) {
            this.props.close();          // close dialog
            this.props.onSuccess();      // continue action
        } else {
            this.state.error = true;
        }
    }
}

const originalStart = actionService.start;

patch(actionService, {
    start(env, ...args) {
        
        // call original start → gives the manager (with doAction)
        const service = originalStart.call(this, env, ...args);
        const originalDoAction = service.doAction;

        service.doAction = async function (actionRequest, options = {}) {
            const action = await service.loadAction(actionRequest, options.additionalContext);
            if (action?.name != "Point of Sale" && action?.type === "ir.actions.act_window" && this.currentController?.displayName === "Home") {
                const expectedPassword = await env.services.orm.call(
                    "ir.config_parameter",
                    "get_param",
                    ["mezole.pos_password"]
                );
                if (!expectedPassword) {
                    console.warn("No password set in configuration, proceeding without confirmation");
                    return originalDoAction.call(this, actionRequest, options);
                };
                return new Promise((resolve, reject) => {
                env.services.dialog.add(PasswordDialog, {
                expectedPassword,

                onSuccess: async () => {
                    const result = await originalDoAction.call(this, actionRequest, options);
                    resolve(result);
                },

                close: () => reject(),  // cancel action
            });
                });
            }
            else {

            return originalDoAction.call(this, actionRequest, options);
            }
        };

        return service;
    },
});