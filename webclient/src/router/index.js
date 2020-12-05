import React from 'react'
import { Route, Switch } from 'react-router'
import routerconfig from '../config/routerconfig'
import Container from '../components/container'

const Router = () => (
    <Route path="/">
        <Container>
            <Switch>
                {routerconfig.map(
                    route => (
                        <Route key={route.path} path={route.path}>
                            {route.component}
                        </Route>
                    )
                )}
            </Switch>
        </Container>
    </Route>
)
export default Router