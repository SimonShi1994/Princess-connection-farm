import React from 'react'
import { TimePicker, Input, Select, Row, Col } from 'antd';
import moment from 'moment';
const { Option } = Select;

const { RangePicker } = TimePicker;

export default ({ value = {}, onChange }) => {
    const [time, setTime] = React.useState([0, 0]);
    const [can, setCan] = React.useState('18015879305');
    const [type, settype] = React.useState(1)
    React.useEffect(() => {
        if (typeof value === 'object') {
            settype(1)
            if (Object.keys(value).length < 1) {
                settype(3)
            }
        }
    })
    const triggerChange = (changedValue) => {
        let val = changedValue
        if (typeof changedValue === 'object') {
            val = {
                start_hour: changedValue[0].hour(),
                end_hour: changedValue[1].hour()
            }
            setTime(val.start_hour, val.end_hour)
        } else {
            setCan(changedValue)
        }
        if (onChange) {
            onChange({ ...value, ...val });
        }
    };
    if (value.can_juanzeng) {
        return (
            <div><Input value={value.can_juanzeng || can} onChange={triggerChange} /></div>
        )
    }
    return (
        <div>
            <Row gutter={8}>
                <Col span={8}>
                    <Select value={type} onChange={settype}>
                        <Option value={1}>指定时间段</Option>
                        <Option value={2}>可以捐赠</Option>
                        <Option value={3}>无条件</Option>
                    </Select>
                </Col>
                <Col span={16}>
                    {type === 1 ? (<RangePicker format="HH" value={[moment().hour(value.start_hour || time[0]), moment().hour(value.end_hour || time[1])]} order={false} onChange={triggerChange} />) : (<Input disabled={type == 3 ? true : false} onChange={triggerChange} />)}
                </Col>
            </Row>
        </div>
    )
}