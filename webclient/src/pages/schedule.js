import example from '../example/schedule.json'
import React from 'react'
import Schedulelist from '../components/Schedulelist/index'
import { Collapse, List } from 'antd';

const { Panel } = Collapse;
export default () => {
    return (
        <div>
            <Collapse>
                {example.map((s, i) => (
                    <Panel header="This is panel header 1" key={i}>
                        <List
                            size="large"
                            bordered
                            dataSource={s.schedules}
                            renderItem={(item, index) => <Schedulelist {...item} index={[i,index]} />}
                        />
                    </Panel>
                ))}
            </Collapse>
        </div>
    )
}