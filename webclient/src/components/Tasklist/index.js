import React from 'react'
import { List, Table } from 'antd';
import transformTask from '../../utils/transformTask'

const columns = [
    {
        title: '任务名',
        dataIndex: 'title',
        key: 'name',
    },
    {
        title: '任务描述',
        dataIndex: 'desc',
        key: 'age',
        width: '40%',
    },
];
export default (props) => {
    const { tasklist, schema } = props
    const expandedRowRender = (record) => {
        console.log(record)
        const columns = [
            {
                title: '子参数',
                dataIndex: 'title',
                key: 'name',
                width: '10%',
            },
            {
                title: '子参数描述',
                dataIndex: 'desc',
                key: 'age',
            },
            {
                title: '子参数值',
                dataIndex: 'value',
                key: 'value',
                width: '30%',
                editable: true,
            },
        ]
        return <Table columns={columns} dataSource={record.subtasks} pagination={false} />;
    };
    return (
        <List.Item>
            <List.Item.Meta
                description={
                    <>
                        <Table
                            pagination={false}
                            dataSource={(transformTask(tasklist))}
                            expandable={{ expandedRowRender }}
                            rowKey={(record) => `${record.key}`}
                            columns={columns} />;
                    </>
                }
            />
        </List.Item>
    )
}