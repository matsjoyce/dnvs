import * as Alt from "alt";
import $ from "jquery";

var alt = new Alt();

function fetchAndCall(url, func) {
    $.getJSON(url).then(data => func(data));
}

class DataActions {
    connectWS() {
        return (dispatch) => {
            dispatch();
            this.websocket = new WebSocket("ws://" + window.location.host + "/api/ws/broadcast");
            this.websocket.onopen = () => {
                DATA_ACTIONS.refetchJobs();
                DATA_ACTIONS.refetchWorkers();
            };
            this.websocket.onmessage = this.updateFromWS;
            this.websocket.onclose = () => {
                this.updateJobs([]);
                this.updateWorkers([]);
                window.setTimeout(DATA_ACTIONS.connectWS, 5000);
            }
        }
    }
    updateFromWS(message) {
        return JSON.parse(message.data);
    }
    updateJobs(data) {
        return data;
    }
    refetchJobs() {
        return (dispatch) => {
            dispatch();
            fetchAndCall("/api/job/", data => this.updateJobs(data.data.jobs));
        }
    }
    updateWorkers(data) {
        return data;
    }
    refetchWorkers() {
        return (dispatch) => {
            dispatch();
            fetchAndCall("/api/worker/", data => this.updateWorkers(data.data.workers));
        }
    }
}

export var DATA_ACTIONS = alt.createActions(DataActions);

class DataStore {
    constructor() {
        this.bindListeners({
            handleUpdateFromWS: DATA_ACTIONS.UPDATE_FROM_WS,

            handleUpdateJobs: DATA_ACTIONS.UPDATE_JOBS,
            handleRefetchJobs: DATA_ACTIONS.REFETCH_JOBS,

            handleUpdateWorkers: DATA_ACTIONS.UPDATE_WORKERS,
            handleRefetchWorkers: DATA_ACTIONS.REFETCH_WORKERS,
        });
        this.jobs = {};
        this.workers = {};
    }

    handleUpdateFromWS(data) {
        if (data.type == "worker") {
            this.workers[data.data.id] = data.data;
        }
        else if (data.type == "job") {
            this.jobs[data.data.id] = data.data;
        }
        else {
            console.log(data)
        }
    }

    handleUpdateJobs(data) {
        this.jobs = {};
        data.map(job => this.jobs[job.id] = job);
    }
    handleRefetchJobs() {
        this.jobs = {};
    }
    handleUpdateWorkers(data) {
        this.workers = {};
        data.map(worker => this.workers[worker.id] = worker);
    }
    handleRefetchWorkers() {
        this.workers = {};
    }

    getWorker(id) {
        return this.workers[id] || {};
    }
    getJob(id) {
        return this.jobs[id] || {};
    }
}

export var DATA_STORE = alt.createStore(DataStore, 'DataStore');
DATA_ACTIONS.connectWS();
