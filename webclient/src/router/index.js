import React from 'react'
import {Route, Switch} from 'react-router'
import routerconfig from '../config/routerconfig'
import Container from '../components/container'

const Router = () => (
  <Route path="/">
    <Container>
      <Switch>
        {routerconfig.map(
          route => (
            <Route key={route.path} path={route.path} exact render={props => (
              // pass the sub-routes down to keep nesting
              <route.component {...props} />
            )}/>
          )
        )}
      </Switch>
    </Container>
  </Route>
)
export default Router
