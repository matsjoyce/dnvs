import React from "react";

import { DATA_ACTIONS, DATA_STORE } from "./store.jsx";
import { isSetsEqual } from "./utils.jsx";


export class ItemView extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            ids: new Set()
        };
        this.onChange = this.onChange.bind(this);
    }

    componentDidMount() {
        DATA_STORE.listen(this.onChange);
        this.setState({
            ids: new Set(Object.keys(this.getValues(DATA_STORE.state)))
        });
    }

    componentWillUnmount() {
        DATA_STORE.unlisten(this.onChange);
    }

    onChange(state) {
        var new_ids = new Set(Object.keys(this.getValues(state)));
        if (!isSetsEqual(new_ids, this.state.ids)) {
            this.setState({
                ids: new_ids
            });
        }
    }

    render() {
        var Cls = this.itemCls;
        console.log(this.state.ids)
        return <>
            {[...this.state.ids].sort((a, b) => a - b).map(id => <Cls key={id} id={id} initial_expanded={true} collapseable={false} />)}
        </>;
    }
}
