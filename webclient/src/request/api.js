import {get, post, put, del} from './http'

export const listAccount = () => get('/account')
export const retrieveAccount = (username) => get('/account' + '/' + username)
export const createAccount = (username, password) => post('/account', {username: username, password: password})
export const updateAccount = (username, password) => put('/account' + '/' + username, {password: password})
export const deleteAccount = (username) => del('/account' + '/' + username)
