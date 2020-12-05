import React from 'react'
import { Table, Button } from 'antd';
import request from '../request'
const columns = [
    {
        title: '账号',
        dataIndex: 'username',
        key: 'username',
    },
    {
        title: '密码',
        dataIndex: 'password',
        key: 'password',
        editable:true,
    },
    {
        title: '操作',
        dataIndex: 'address',
        key: 'address',
    },
];
export default () => {
    let [data, setData] = React.useState(null);

    React.useEffect(() => {
        async function temp() {
            const { data } = await request('/account')
            setData(data.map(i => {
                return {
                    ...i,
                    key: i.username
                }
            }));
        }
        temp();
    }, [])
    return (
        <div>
            <div>账号列表 <Button>新增</Button></div>
            <Table dataSource={data} columns={columns} ></Table>
        </div>
    )
}