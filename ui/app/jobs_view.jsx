import React from "react";

import { DATA_ACTIONS, DATA_STORE } from "./store.jsx";
import { isSetsEqual, nullOrUndefined, ifNotNU } from "./utils.jsx";
import { Item, ItemTable, ItemTableRow } from "./item.jsx";
import { Worker } from "./workers_view.jsx";


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
        return "warning";
    }

    renderExpanded() {
        return <div className="item" onClick={this.collapse}>
            <div className="item-name">{this.idFormat(this.state.data.id)}</div>
            <ItemTable>
                <ItemTableRow name="State" value={
                    <span className={"text-" + this.color_for_state()}>{this.state.data.state}</span>
                }/>
                <ItemTableRow name="Performed By" value={
                    ifNotNU(this.state.data.performed_by, id => <Worker id={id} key={id} />)
                }/>
            </ItemTable>
        </div>;
    }
}


export class JobsView extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            job_ids: new Set()
        };
        this.onChange = this.onChange.bind(this);
    }

    componentDidMount() {
        DATA_STORE.listen(this.onChange);
        this.setState({
            job_ids: new Set(Object.keys(DATA_STORE.state.jobs))
        });
    }

    componentWillUnmount() {
        DATA_STORE.unlisten(this.onChange);
    }

    onChange(state) {
        var new_ids = new Set(Object.keys(state.jobs));
        if (!isSetsEqual(new_ids, this.state.job_ids)) {
            this.setState({
                job_ids: new_ids
            });
        }
    }

    render() {
        console.log("RJV", this.state.job_ids);
        return <>
            {[...this.state.job_ids].sort((a, b) => a - b).map(id => <Job key={id} id={id} initial_expanded={true} collapseable={false} />)}
        </>;
    }
}
