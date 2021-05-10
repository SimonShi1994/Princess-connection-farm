import React from 'react'
import { Layout, Menu, Breadcrumb } from 'antd';
import { Link } from 'react-router-dom'
const { Header, Content } = Layout;
const menu = [
  {
    key: '1',
    link: '/account',
    description: '账号',
  },
  {
    key: '2',
    link: '/schedule',
    description: '计划',
  },
  {
    key: '3',
    link: '/task',
    description: '任务',
  }
]
const Container = (props) => {
  const [index, setindex] = React.useState('1')
  React.useEffect(() => {
    const { hash } = window.location
    const [_, path] = hash.split('/')
    const dataindex = menu.findIndex(m => m.link === `/${path}`) + 1 + ''
    setindex(dataindex)
    if(!path){
      setindex('1')
    }
  })
  return (
    <>
      <Layout className="layout">
        <Header>
          <div className="logo" />
          <Menu theme="dark" mode="horizontal" selectedKeys={[index]} onClick={(item, key) => { setindex(key) }}>
            {menu.map(m => (
              <Menu.Item key={m.key}><Link to={m.link}>{m.description}</Link></Menu.Item>
            ))}
          </Menu>
        </Header>
        <Content style={{ padding: '0 50px' }}>
          <div className="site-layout-content">{props.children}</div>
        </Content>
      </Layout>
    </>
  )
}

export default Container