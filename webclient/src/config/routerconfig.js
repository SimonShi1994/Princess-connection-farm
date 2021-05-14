import React from 'react'
import Account from "pages/account"
import Schedule from 'pages/schedule'
import Task from 'pages/task'
import ScheduleEdit from 'pages/schedule/edit'
 
export default [
    {
        path:"/",
        component: Account
    },
    {
        path:"/account",
        component: Account
    },
    {
        path:"/schedule",
        component: Schedule
    },
    {
        path:"/schedule/edit/:id",
        component: ScheduleEdit
    },
    {
        path:"/task",
        component: Task
    },
]