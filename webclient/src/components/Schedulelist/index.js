import React from 'react'
import { List } from 'antd';

export default (props) => {
    const { name, record, type, condition, batchlist } = props
    console.log(props)
    return (
        <List.Item>{`计划名${name}`}{`计划类型：${type}`}{condition ? `触发时间${condition.start_hour}-${condition.end_hour}` : null}{batchlist ? `batchlist:${batchlist}` : null}{record ? `记录:${record}` : null}</List.Item>
    )
}