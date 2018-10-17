import React from "react";

import { DATA_ACTIONS, DATA_STORE } from "./store.jsx";
import { nullOrUndefined, withDefault, ifNotNU, react_join } from "./utils.jsx";
import { Item, ItemTable, ItemTableRow } from "./item.jsx";
import { ItemView } from "./item_view.jsx";
import { Job } from "./jobs_view.jsx";
import { Plugin } from "./plugins_view.jsx";


export class Worker extends Item {
    getValue = state => state.getWorker(this.props.id);
    idFormat = x => "W-" + x;

    color_for_state() {
        if (this.state.data.state == "working") {
            return "success";
        }
        else if (this.state.data.state == "considering") {
            return "primary";
        }
        else if (this.state.data.state == "idle") {
            return "info";
        }
        else if (this.state.data.state == "disconnected") {
            return "danger";
        }
        return "warning";
    }

    renderSemiCollapsedText() {
        return <>
            {this.state.data.address}
            {ifNotNU(this.state.data.plugins, ws => ws.length == 0 ? null : <span className="text-light"> [{ws.length} plugin(s)]</span>)}
            {ifNotNU(this.state.data.warnings, ws => ws.length == 0 ? null : <span className="text-warning"> [{ws.length} warning(s)]</span>)}
        </>;
    }

    renderExpanded() {
        return <div className="item" onClick={this.collapse}>
            <div className="item-name">{this.idFormat(this.state.data.id)}</div>
            <ItemTable>
                <ItemTableRow name="State" value={
                    <span className={"text-" + this.color_for_state()}>{this.state.data.state}</span>
                }/>
                <ItemTableRow name="Address" value={this.state.data.address}/>
                <ItemTableRow name="Current Job" value={
                    ifNotNU(this.state.data.current_job, id => <Job id={id} key={id} />)
                }/>
                <ItemTableRow name="Considering Job" value={
                    ifNotNU(this.state.data.considering_job, id => <Job id={id} key={id} />)
                }/>
                <ItemTableRow name="Plugins" value={
                    ifNotNU(this.state.data.plugins, ps => react_join(ps.map(id => <Plugin id={id} key={id} />)))
                }/>
                <ItemTableRow name="Warnings" value={
                    ifNotNU(this.state.data.warnings, ws => ws.length == 0 ? null : ws.map((v, i) =>
                        <div key={i} className="text-warning">{v}</div>
                    )
                )}/>
            </ItemTable>
        </div>;
    }
}


export class WorkersView extends ItemView {
    getValues = state => state.workers;
    itemCls = Worker;
}
