import React from 'react'
import { Select } from 'antd';
import request from '../../../request.js'

export default ({ value = {}, onChange }) => {
    const [batch, setBatch] = React.useState([]);
    const [options, updateoptions] = React.useState([])

    React.useEffect(() => {
        async function getoptions() {
            const { data } = await request(`/batches`)
            updateoptions(data.map(a => {
                return { label: a, value: a }
            }))
        }
        getoptions()
        if (typeof value === "string") {
            setBatch(value)
        }
        // 防止切换类型过来是{}的情况
        else if (JSON.stringify(value) === "{}"){
            setBatch([])
        }
        else{
            setBatch(value.split(','))
        }
    }, [])
    const triggerChange = (changedValue) => {
        setBatch(changedValue)
        if (onChange) {
            onChange(changedValue.join(','));
        }
    };
    return (
        <Select
            mode="multiple"
            allowClear
            placeholder="Please select"
            value={batch}
            options={options}
            onChange={triggerChange}
        >
        </Select>
    )
}