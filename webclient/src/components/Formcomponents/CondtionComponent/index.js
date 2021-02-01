import React from 'react'
import { TimePicker, Input, Select } from 'antd';
import moment from 'moment';
const { Option } = Select;

const { RangePicker } = TimePicker;

export default ({ value = {}, onChange }) => {
    const [time, setTime] = React.useState([0, 0]);
    const [can, setCan] = React.useState('18015879305');
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
            <Select>
            <Option value="1">指定时间段</Option>
            <Option value="2">可以捐赠</Option>
            </Select>
            
            <RangePicker format="HH" value={[moment().hour(value.start_hour || time[0]), moment().hour(value.end_hour || time[1])]} order={false} onChange={triggerChange} /></div>
    )
}