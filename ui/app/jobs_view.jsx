import React from "react";

import { DATA_ACTIONS, DATA_STORE } from "./store.jsx";
import { nullOrUndefined, withDefault, ifNotNU, react_join } from "./utils.jsx";
import { Item, ItemTable, ItemTableRow } from "./item.jsx";
import { ItemView } from "./item_view.jsx";
import { Worker } from "./workers_view.jsx";
import { Plugin } from "./plugins_view.jsx";


export class Job extends Item {
    getValue = state => state.getJob(this.props.id);
    idFormat = x => "J-" + x;

    color_for_state() {
        if (this.state.data.state == "finished") {
            return "success";
        }
        else if (this.state.data.state == "running") {
            return "info";
        }
        else if (this.state.data.state == "pending") {
            return "light";
        }
        else if (this.state.data.state == "failed") {
            return "danger";
        }
        else if (this.state.data.state == "consideration") {
            return "primary";
        }
        return "warning";
    }

    renderSemiCollapsedText() {
        return this.state.data.plugin;
    }

    renderExpanded() {
        return <div className="item" onClick={this.collapse}>
            <div className="item-name">{this.idFormat(this.state.data.id)}</div>
            <ItemTable>
                <ItemTableRow name="State" value={
                    <span className={"text-" + this.color_for_state()}>{this.state.data.state}</span>
                }/>
                <ItemTableRow name="Plugin" value={
                    ifNotNU(this.state.data.plugin, id => <Plugin id={id} key={id} />)
                }/>
                <ItemTableRow name="Performed by" value={
                    ifNotNU(this.state.data.performed_by, id => <Worker id={id} key={id} />)
                }/>
                <ItemTableRow name="Rejected by" value={
                    ifNotNU(this.state.data.rejected_by, rb => rb.length == 0 ? null : react_join(rb.map(id => <Worker id={id} key={id} />)))
                }/>
            </ItemTable>
        </div>;
    }
}


export class JobsView extends ItemView {
    getValues = state => state.jobs;
    itemCls = Job;
}
