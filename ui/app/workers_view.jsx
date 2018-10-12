import React from "react";

import { DATA_ACTIONS, DATA_STORE } from "./store.jsx";
import { isSetsEqual, nullOrUndefined, withDefault, ifNotNU } from "./utils.jsx";
import { Item, ItemTable, ItemTableRow } from "./item.jsx";
import { Job } from "./jobs_view.jsx";


export class Worker extends Item {
    getValue = state => state.getWorker(this.props.id);
    idFormat = x => "W-" + x;

    color_for_state() {
        if (this.state.data.state == "working") {
            return "info";
        }
        else if (this.state.data.state == "considering") {
            return "info";
        }
        else if (this.state.data.state == "idle") {
            return "success";
        }
        else if (this.state.data.state == "disconnected") {
            return "danger";
        }
        return "warning";
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
            </ItemTable>
        </div>;
    }
}


export class WorkersView extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            worker_ids: new Set()
        };
        this.onChange = this.onChange.bind(this);
    }

    componentDidMount() {
        DATA_STORE.listen(this.onChange);
        this.setState({
            worker_ids: new Set(Object.keys(DATA_STORE.state.workers))
        });
    }

    componentWillUnmount() {
        DATA_STORE.unlisten(this.onChange);
    }

    onChange(state) {
        var new_ids = new Set(Object.keys(state.workers));
        if (!isSetsEqual(new_ids, this.state.worker_ids)) {
            this.setState({
                worker_ids: new_ids
            });
        }
    }

    render() {
        console.log("WJV", this.state.worker_ids);
        return <>
            {[...this.state.worker_ids].sort().map(id => <Worker key={id} id={id} initial_expanded={true} collapseable={false} />)}
        </>;
    }
}

