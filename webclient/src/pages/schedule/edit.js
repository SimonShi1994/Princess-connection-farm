import React from 'react'
import request from '../../request'
import ConditionComponent from '@/components/Formcomponents/CondtionComponent'
import Batchlist from '@/components/Formcomponents/Batchlist'
import { Form, Input, Button, Card, InputNumber, Row, Col, Radio } from 'antd';

const layout = {
    labelCol: { span: 8 },
    wrapperCol: { span: 8 },
};


const options = [
    { value: 'asap', label: '立即完成' },
    { value: 'wait', label: '等待执行' },
    { value: 'config', label: '配置任务' },
];
export default (props) => {
    const { id } = props.match.params
    const [schedules, updateschedules] = React.useState([])
    React.useEffect(() => {
        async function temp() {
            const { data } = await request(`/get_schedules/${id}`)
            updateschedules(data.schedules)
        }
        temp();
    }, [])
    const handlechange = (index, value) => {
        const temp = [...schedules]
        temp[index] = value
        updateschedules(temp)
    }
    const onFinish = async (values) => {
        await request(`/schedules_save`, {
            method: 'post', data: {
                ...values,
                "filename": id,
            }
        })
    }
    console.log(schedules)
    return (
        <div>
            <Card title={id}>
                {schedules.map((schedule, index) => {
                    switch (schedule.type) {
                        case 'asap':
                            return (
                                <Asapform updateschedules={handlechange} onFinish={onFinish} key={index} index={index} {...schedule} />
                            );
                        case 'config':
                            return (
                                <Configform updateschedules={handlechange} onFinish={onFinish} key={index} index={index} {...schedule} />
                            )
                        case 'wait':
                            return (
                                <Waitconfig updateschedules={handlechange} onFinish={onFinish} key={index} index={index} {...schedule} />
                            )
                        default:
                            return;
                    }
                }
                )}
            </Card>

        </div>
    )
}

// # 立刻执行计划
// # schedule被执行时，如果condition满足，则立刻将该batch解析放入任务队列
// # 如果condition不满足，则跳过该batch。
// # 例子：制定两个schedule，一个早上执行，一个晚上执行
// # 希望早上start schedule时执行早上任务，晚上start schedule时执行晚上任务
// # 则可以创建两个asap计划，其中一个的condition定在5~12，一个定在12~29
// # 此时若早上执行，第一个计划condition满足，立刻执行；第二个不满足，不执行。
// # 若晚上执行，第一个计划contidion不满足，不执行，第二个满足，执行。
// {
//     "type":"asap"  # As soon as possible
//     "name":"..."
//     "batchfile":"..."  # batch文件所在位置
//     "batchlist":[
//         # 为40 to 1设计，多个batch依次执行，两个batch之间清空记录
//         # 若一个batch未成功运行，则后一个batch也不会运行。
//         # batchlist和batchfile只应该存在一个。
//         "...",
//         "...",
//         ...
//     ]
//     ”condition”:{
//         # condition为条件，对asap任务，只有condition全部满足，才会执行。
//         # condition可以是一个空字典，表示不设置条件
//         "start_hour":int  # 小时开始，只有小时数>start_hour时才会执行任务
//         "end_hour":int  # 小时结束，只有小时数<end_hour时才会执行任务
//         "can_juanzeng":account  # account可以发起捐赠了
//         "_last_rec":dir  # 用户无法编辑、查看此条。_last_rec文件夹下无_fin文件时执行。
//         # 还可以补充其它condition，但暂时没想到。
//     }
//     "record":int  # 记录模式
// }

const Asapform = (props) => {

    const { updateschedules, index, onFinish } = props
    const handlechange = (_, values) => {
        updateschedules(index, values)
    }
    return (
        <Form
            {...layout}
            name={props.name}
            key={props.name}
            initialValues={props}
            onFinish={onFinish}
            onValuesChange={handlechange}
        >
            <Form.Item
                label="计划名"
                name="name"
                rules={[{ required: true, message: '请输入计划名' }]}
            >
                <Input />
            </Form.Item>
            <Form.Item
                label="batchlist"
                name="batchlist"
                rules={[{ required: true, message: 'Please input your batchlist!' }]}
            >
                <Batchlist />
            </Form.Item>
            <Form.Item
                label="condition"
                name="condition"
            >
                <ConditionComponent />
            </Form.Item>
            <Form.Item
                label="类型"
                name="type"
                rules={[{ required: true, message: 'Please input your type!' }]}
            >
                <Radio.Group
                    options={options}
                    optionType="button"
                    buttonStyle="solid"
                />
            </Form.Item>

            <Row>
                <Col offset={7} span={8}>
                    <Button type="primary" htmlType="submit">
                        保存
                     </Button>
                </Col>
            </Row>
        </Form>
    )
}

const Configform = (props) => {
    const { index, updateschedules, onFinish } = props
    const handlechange = (_, values) => {
        updateschedules(index, values)
    }
    return (
        <Form
            {...layout}
            name={`config${index}`}
            key={`config${index}`}
            initialValues={props}
            onFinish={onFinish}
            onValuesChange={handlechange}
        >
            <Row><Col offset={4} span={8}>Config</Col></Row>
            <Form.Item
                label="每天清理记录的时间"
                name="restart"
                rules={[{ required: true, message: '请输入清理记录时间' }]}
            >
                <InputNumber max={24} min={0} />
            </Form.Item>
            <Form.Item
                label="类型"
                name="type"
                rules={[{ required: true, message: 'Please input your batchfile!' }]}
            >
                <Radio.Group
                    options={options}
                    optionType="button"
                    buttonStyle="solid"
                />
            </Form.Item>

            <Row>
                <Col offset={7} span={8}>
                    <Button type="primary" htmlType="submit">
                        保存
                     </Button>
                </Col>
            </Row>
        </Form>)
}
// # 等待执行计划
// # schedule执行时，首先将所有的asap计划加入任务队列
// # 如果有等待执行计划，则schedule持续运行，直到指定条件出现。
// # 应用场景 1：自动发起捐赠。可以设置condition为can_juanzeng，则
// # 当指定账号可以捐赠时，自动将该batch放入任务队列。
// # 发起捐赠可以设置为高优先级，从而可以插队执行。
// # 应用场景 2：24h挂机。可以设置condition为时间段，则
// # 当到达指定时间段后，自动将该batch加入任务队列。
// {
//     "type":"wait"
//     "name":"..."
//     "batchfile":"..."
//     "batchlist":["...","...",...]
//     "condition":{...}
//     "record":int
// }
const Waitconfig = (props) => {
    const { updateschedules, index, onFinish } = props
    const handlechange = (_, values) => {
        updateschedules(index, values)
    }
    return (
        <Form
            {...layout}
            name={props.name}
            key={props.name}
            initialValues={props}
            onFinish={onFinish}
            onValuesChange={handlechange}
        >
            <Form.Item
                label="计划名"
                name="name"
                rules={[{ required: true, message: '请输入计划名' }]}
            >
                <Input />
            </Form.Item>
            <Form.Item
                label="batchlist"
                name="batchlist"
                rules={[{ required: true, message: 'Please input your batchlist!' }]}
            >
                <Batchlist />
            </Form.Item>
            <Form.Item
                label="record"
                name="record"
                rules={[{ required: true, message: 'Please input your record!' }]}
            >
                <InputNumber />
            </Form.Item>
            <Form.Item
                label="condition"
                name="condition"
            >
                <ConditionComponent />
            </Form.Item>
            <Form.Item
                label="类型"
                name="type"
                rules={[{ required: true, message: 'Please input your batchfile!' }]}
            >
                <Radio.Group
                    options={options}
                    optionType="button"
                    buttonStyle="solid"
                />
            </Form.Item>

            <Row>
                <Col offset={7} span={8}>
                    <Button type="primary" htmlType="submit">
                        保存
                     </Button>
                </Col>
            </Row>
        </Form>
    )
}