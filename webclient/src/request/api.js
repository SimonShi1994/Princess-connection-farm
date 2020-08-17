import {get, post, put, del} from './http'

export const listAccount = () => get('/account')
export const retrieveAccount = (username) => get('/account' + '/' + username)
export const createAccount = (username, password, taskname) => post('/account', {username: username, password: password, taskname: taskname})
export const updateAccount = (username, password, taskname) => put('/account' + '/' + username, {password: password, taskname: taskname})
export const deleteAccount = (username) => del('/account' + '/' + username)

export const listTask = () => get('/task')
export const retrieveTask = (taskname) => get('/task' + '/' + taskname)
export const createTask = (taskname) => post('/task', {taskname: taskname})
export const updateTask = (taskname, subtasks) => put('/task' + '/' + taskname, {subtask: subtasks})
export const deleteTask = (taskname) => del('/task' + '/' + taskname)

export const listSubtaskSchema = () => get('/subtask/schema')
export const retrieveSubtaskSchema = (abbr) => get('/subtask/schema' + '/' + abbr)
