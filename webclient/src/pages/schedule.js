import React from 'react'
import Schedulelist from '../components/Schedulelist/index'
import { Button, Collapse, List, message } from 'antd';
import ProForm, { ModalForm, ProFormText, } from '@ant-design/pro-form';
import request from '../request'

const { Panel } = Collapse;
export default () => {
    const [list, setlist] = React.useState([])
    const [listdata, setdata] = React.useState([])
    React.useEffect(() => {
        async function temp() {
            const { data } = await request('/schedules')
            setlist(data)
        }
        temp();
    }, [])
    const getdata = async (index) => {
        const copy = [...listdata]
        const { data } = await request(`/get_schedules/${list[index]}`)
        copy[index] = data.schedules
        setdata(copy)
    }
    return (
        <div>
            <Collapse onChange={getdata} accordion>
                {list.map((s, i) => (
                    <Panel header={s} key={i}>
                        <List
                            size="large"
                            bordered
                            dataSource={listdata[i] || []}
                            renderItem={(item, index) => <Schedulelist {...item} schedulename={s} />}
                        />
                    </Panel>
                ))}
            </Collapse>
            <ModalForm
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
            </ModalForm>
        </div >
    )
}