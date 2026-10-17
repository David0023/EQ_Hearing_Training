import { publicApi } from "../../../api/client";

export function get_frequencies () {
    return publicApi.get('/api/v1/training/infos/frequency/groups')
}

export function get_gain_options () {
    return publicApi.get('/api/v1/training/infos/gain/options')
}
