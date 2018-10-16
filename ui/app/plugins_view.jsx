import React from "react";

import { DATA_ACTIONS, DATA_STORE } from "./store.jsx";
import { nullOrUndefined, withDefault, ifNotNU, react_join } from "./utils.jsx";
import { Item, ItemTable, ItemTableRow } from "./item.jsx";
import { ItemView } from "./item_view.jsx";
import { Worker } from "./workers_view.jsx";


export class Plugin extends Item {
    getValue = state => state.getPlugin(this.props.id);
    idFormat = x => x;

    color_for_state() {
        return "light";
    }

    renderExpanded() {
        return <div className="item" onClick={this.collapse}>
            <div className="item-name">{this.idFormat(this.state.data.id)}</div>
            <ItemTable>
                <ItemTableRow name="Version" value={this.state.data.version}/>
                <ItemTableRow name="Supporting workers" value={
                    ifNotNU(this.state.data.workers, ws => react_join(ws.sort((a, b) => a - b).map(id => <Worker id={id} key={id} />), i => ", "))
                }/>
            </ItemTable>
        </div>;
    }
}


export class PluginsView extends ItemView {
    getValues = state => state.plugins;
    itemCls = Plugin;
}

