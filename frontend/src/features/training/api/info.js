import { publicApi } from "../../../api/client";

export function getFrequencies () {
    return publicApi.get('/api/v1/training/infos/frequency/groups')
}

export function getGainOptions () {
    return publicApi.get('/api/v1/training/infos/gain/options')
}
