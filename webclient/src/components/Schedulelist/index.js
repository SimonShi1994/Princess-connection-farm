import React from 'react'
import { List } from 'antd';
import transformState from '../../utils/transformState'
import { Link } from 'react-router-dom'

export default (props) => {
    const { name, record, type, condition, batchlist,index } = props
    return (
        <List.Item> <List.Item.Meta
            title={<Link to={`/schedule/edit/${index[0]}`}>计划名：{name ? name : '未配置计划名'}</Link>}
            description={<>{`计划类型：${transformState(type)}`} {condition && condition.start_hour ? `触发时间段：${condition.start_hour}-${condition.end_hour}` : null}{batchlist ? `批配置：${batchlist}` : null} {record ? `记录：${record}` : null}</>}
        /> </List.Item>
    )
}