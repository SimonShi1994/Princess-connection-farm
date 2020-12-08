import React from 'react'
import { Layout, Menu, Breadcrumb } from 'antd';
import { Link } from 'react-router-dom'
const { Header, Content } = Layout;

const Container = (props) => {
  const [index, setindex] = React.useState('1')
  return (
    <>
      <Layout className="layout">
        <Header>
          <div className="logo" />
          <Menu theme="dark" mode="horizontal" defaultSelectedKeys={index} onClick={(item, key,) => { setindex(key) }}>
            <Menu.Item key="1"><Link to="/account">账号</Link></Menu.Item>
            <Menu.Item key="2"><Link to="/schedule">计划</Link></Menu.Item>
          </Menu>
        </Header>
        <Content style={{ padding: '0 50px' }}>
          {/* <Breadcrumb style={{ margin: '16px 0' }}>
        <Breadcrumb.Item>Home</Breadcrumb.Item>
        <Breadcrumb.Item>List</Breadcrumb.Item>
        <Breadcrumb.Item>App</Breadcrumb.Item>
      </Breadcrumb> */}

          <div className="site-layout-content">{props.children}</div>
        </Content>
      </Layout>
    </>
  )
}

export default Container