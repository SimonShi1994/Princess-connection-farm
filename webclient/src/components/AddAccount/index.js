import React from 'react';
import { Button, message } from 'antd';
import { ModalForm, ProFormText } from '@ant-design/pro-form';
import { PlusOutlined } from '@ant-design/icons';

export default (props) => {
    const { onFinish } = props
    return (
        <ModalForm
            title="新建账号"
            trigger={
                <Button type="primary">
                    <PlusOutlined />
            新建账号
        </Button>
            }
            // modalProps={{
            //     onCancel: () => console.log('run'),
            // }}
            onFinish={onFinish}
        >
            <ProFormText name="username" label="账号" initialValue="123" />
            <ProFormText name="password" label="密码" initialValue="" />
        </ModalForm>
    );
};