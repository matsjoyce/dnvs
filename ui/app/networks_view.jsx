import React from "react";

import { DATA_ACTIONS, DATA_STORE } from "./store.jsx";
import { nullOrUndefined, withDefault, ifNotNU, react_join } from "./utils.jsx";
import { Item, ItemTable, ItemTableRow } from "./item.jsx";
import { ItemView } from "./item_view.jsx";
import { Plugin } from "./plugins_view.jsx";
import { Job } from "./jobs_view.jsx";


export class Network extends Item {
    getValue = state => state.getNetwork(this.props.id);
    idFormat = x => "S-" + x;

    color_for_state() {
        return "light";
    }

    renderSemiCollapsedText() {
        return <>
            {this.state.data.network}
            {ifNotNU(this.state.data.active_jobs, js => js.length == 0 ? null : <span className="text-light"> [{js.length} active job(s)]</span>)}
        </>;
    }

    renderExpanded() {
        return <div className="item" onClick={this.collapse}>
            <div className="item-name">{this.idFormat(this.state.data.id)}</div>
            <ItemTable>
                <ItemTableRow name="Network" value={this.state.data.network}/>
                <ItemTableRow name="Addresses" value={this.state.data.addresses}/>
                <ItemTableRow name="Protocol" value={"IPv" + this.state.data.protocol}/>
                <ItemTableRow name="Active plugins" value={
                    ifNotNU(this.state.data.active_plugins, ps => ps.length == 0 ? null : react_join(ps.map(id => <Plugin id={id} key={id} />)))
                }/>
                <ItemTableRow name="Run plugins" value={
                    ifNotNU(this.state.data.run_plugins, ps => ps.length == 0 ? null : react_join(ps.map(id => <Plugin id={id} key={id} />)))
                }/>
                <ItemTableRow name="Active jobs" value={
                    ifNotNU(this.state.data.active_jobs, js => js.length == 0 ? null : react_join(js.map(id => <Job id={id} key={id} />)))
                }/>
                <ItemTableRow name="All jobs" value={
                    ifNotNU(this.state.data.jobs, js => js.length == 0 ? null : react_join(js.map(id => <Job id={id} key={id} />)))
                }/>
            </ItemTable>
        </div>;
    }
}


export class NetworksView extends ItemView {
    getValues = state => state.networks;
    itemCls = Network;
}
