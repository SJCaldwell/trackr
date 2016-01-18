import React from 'react';
import { render } from 'react-dom';
import Page from './components/page';
import Home from './components/home';

const App = React.createClass({
  getInitialState(){
    return {
      route: window.location.hash.substr(1)
    }
  },

  componentDidMount(){
    window.addEventListener('hashchange', () => {
      this.setState({
        route : window.location.hash.substr(1)
      })
    })
  },

  render(){
    let Child
    switch (this.state.route){
      case '/home': Child = Home; break;
      default:       Child = Page; 
    }

    return(
      <div>
      <Child/>
      </div>
      )
  }
})

export default App;