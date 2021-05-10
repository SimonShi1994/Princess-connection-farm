import React from 'react'
import Tasklist from '../../components/Tasklist/index'
import { Button, Collapse, List, message } from 'antd';
import ProForm, { ModalForm, ProFormText, } from '@ant-design/pro-form';
import request from '../../request'

const { Panel } = Collapse;
export default () => {
    const [list, setlist] = React.useState([])
    const [listdata, setdata] = React.useState([])
    const [schema,updateSchema] = React.useState(localStorage.getItem('schema'))
    React.useEffect(() => {
        async function temp() {
            const { data } = await request('/task')
            console.log(data)
            setlist(data)
            const schemadata = await request('/subtask/schema')
            updateSchema(schemadata.data)
            localStorage.setItem('schema',JSON.stringify(schemadata.data))
        }
        temp();
    }, [])
    const getdata = async (index) => {
        const copy = [...listdata]
        const { data } = await request(`/task/${list[index].taskname}`)
        copy[index] = data.schedules
        setdata(copy)
    }
    return (
        <div>
            <Collapse onChange={getdata} accordion>
                {list.map((s, i) => (
                    <Panel header={s.taskname} key={i}>
                        <List
                            size="large"
                            bordered
                            dataSource={[list[i] ]|| []}
                            renderItem={(item, index) => <Tasklist schema={schema} tasklist={item.subtasks.tasks} />}
                        />
                    </Panel>
                ))}
            </Collapse>
            {/* <ModalForm
                validateMessages={
                    {
                        types: {

                        }
                    }}
                trigger={
                    <Button type="primary" style={{ marginTop: 20 }}>新增Schedule</Button>
                }
                title="新建计划"
                onFinish={async (values) => {
                    console.log(values.name);
                    // 不返回不会关闭弹框
                    const json = {
                        "name": values.name,
                        "batchlist": [],
                        "condition": {},
                        "type": "asap",
                        "filename": values.name
                    }
                    const result = await request(`/schedules_save`, {
                        method: 'post',
                        data: json
                    })

                    if (result.code === 200) {
                        message.success('新增成功')
                    } else {
                        message.error('新增失败')
                    }
                    return true;
                }}
            >
                <ProFormText rules={[
                    {
                        required: true,
                        message: '请填写计划名'
                    },
                    {
                        validator: (_, value) => {
                            return !list.includes(value) ? Promise.resolve() : Promise.reject(new Error('有重复计划名'))
                        }
                    },
                ]} validateTrigger width="sm" name="name" label="计划名" ></ProFormText>
            </ModalForm> */}
        </div >
    )
}