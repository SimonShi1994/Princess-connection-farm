import React from 'react'
import { Table, Input, InputNumber, message, Popconfirm, Form } from 'antd';
import AddAccount from '../components/AddAccount'
import request from '../request'

export default () => {
    const [form] = Form.useForm();
    let [data, setData] = React.useState([]);
    const isEditing = (record) => record.key === editingKey;
    const [editingKey, setEditingKey] = React.useState('');
    const edit = (record) => {
        form.setFieldsValue({ name: '', age: '', address: '', ...record });
        setEditingKey(record.key);
    };

    const cancel = () => {
        setEditingKey('');
    };
    const save = async (key) => {
        try {
            const row = await form.validateFields();

            const newData = [...data];
            const index = newData.findIndex(item => key === item.key);
            if (index > -1) {
                const item = newData[index];
                newData.splice(index, 1, {
                    ...item,
                    ...row,
                });
                setData(newData);
                setEditingKey('');
            } else {
                newData.push(row);
                setData(newData);
                setEditingKey('');
            }
        } catch (errInfo) {
            console.log('Validate Failed:', errInfo);
        }
    };
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
            editable: true,
        },
        {
            title: '操作',
            dataIndex: 'address',
            key: 'address',
            render: (_, record) => {
                const editable = isEditing(record);
                return editable ? (
                    <span>
                        <a onClick={() => save(record.key)} style={{ marginRight: 8 }}>
                            保存
                    </a>
                        <Popconfirm title="确认取消？" onConfirm={cancel}>
                            <a>取消</a>
                        </Popconfirm>
                    </span>
                ) : (
                        <a disabled={editingKey !== ''} onClick={() => edit(record)}>
                            编辑
                        </a>
                    );
            },
        },
    ];
    const EditableCell = ({
        editing,
        dataIndex,
        title,
        inputType,
        record,
        index,
        children,
        ...restProps
    }) => {
        const inputNode = inputType === 'number' ? <InputNumber /> : <Input />;

        return (
            <td {...restProps}>
                {editing ? (
                    <Form.Item
                        name={dataIndex}
                        style={{ margin: 0 }}
                        rules={[
                            {
                                required: true,
                                message: `Please Input ${title}!`,
                            },
                        ]}
                    >
                        {inputNode}
                    </Form.Item>
                ) : (
                        children
                    )}
            </td>
        );
    };
    const addAccount = async (value) => {
        const result = await request('/account', {
            method: 'post',
            data: value
        })
        if(result.msg===""){
            message.success(`添加账号${value.username}成功`)
        }
        return true
    }
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
            <Form form={form} component={false}>
                <div>账号列表 <AddAccount onFinish={addAccount}>新增账号</AddAccount></div>
                <Table
                    pagination={{
                        pageSize: 20
                    }}
                    components={{
                        body: {
                            cell: EditableCell,
                        },
                    }} dataSource={data} columns={columns.map(col => {
                        if (!col.editable) {
                            return col;
                        }
                        return {
                            ...col,
                            onCell: (record) => ({
                                record,
                                inputType: 'text',
                                dataIndex: col.dataIndex,
                                title: col.title,
                                editing: isEditing(record),
                            }),
                        };
                    })} ></Table>
            </Form>
        </div>
    )
}