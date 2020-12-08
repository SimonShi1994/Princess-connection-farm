import example from '../example/schedule.json'
import React from 'react'
import Schedulelist from '../components/Schedulelist/index'
import { List } from 'antd';

export default () => {
    const { schedules } = example
    console.log(schedules)
    return (
        <div>
            <List
                size="large"
                header={<div>Header</div>}
                footer={<div>Footer</div>}
                bordered
                dataSource={schedules}
                renderItem={item => <Schedulelist {...item} />}
            />
        </div>
    )
}