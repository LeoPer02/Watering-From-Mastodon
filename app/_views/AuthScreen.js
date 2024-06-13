
import React, { Component } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Image } from 'react-native';
import { accountService } from '../_services/account';
import Toast from 'react-native-toast-message';

class AuthScreen extends Component {
  constructor(props) {
    super(props);
    this.state = {
      username: '',
      password: '',
      isRegistering: false,
      history: [],
    };
  }

  toggleMode = () => {
    this.setState({ isRegistering: !this.state.isRegistering });
  };

  handleInputChange = (field, value) => {
    this.setState({ [field]: value });
  };

  handleSubmit = () => {
    const { isRegistering, history } = this.state;
    if (isRegistering) {
      accountService.register(this.state.username , this.state.password)
      .then((response)=> {
        console.log(response);
        this.login(this.state.username, this.state.password)
      })
    } else {
      this.login(this.state.username, this.state.password)
    }
  };

  login = (username, password) =>{
    const { history } = this.state;
    accountService.login(username , password)
    .then((response) => {
      console.log(response);
      if(response === undefined){
        history.push({ username, timestamp: new Date().toISOString() });
        this.setState({ history });
        Toast.show({
          type: 'success',
          text1: 'Logged In Successfully',
          text2: `Welcome back, ${username}!`
        });
        this.props.navigation.navigate('Dashboard');
      }
      Toast.show({
        type: 'error',
        text1: response.error,
      });
    })

  }
  render() {
    const { username, password, isRegistering, history } = this.state;

    return (
      <View style={styles.container}>
          <Image source={require('./images/plant.png')} style={styles.image} />
        <Text style={styles.title}>{isRegistering ? 'Register' : 'Login'}</Text>
        <TextInput
          style={styles.input}
          placeholder="Username"
          value={username}
          autoCapitalize="none"
          onChangeText={(value) => this.handleInputChange('username', value)}
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          secureTextEntry
          value={password}
          autoCapitalize="none"
          onChangeText={(value) => this.handleInputChange('password', value)}
        />
        <Button style={styles.mb} title={isRegistering ? 'Register' : 'Login'} onPress={this.handleSubmit} />
        <Text></Text>
        <Button title={isRegistering ? 'Switch to Login' : 'Switch to Register'} onPress={this.toggleMode} />
      </View>
    );
  }
}

const styles = StyleSheet.create({
  mb:{
    marginBottom: 6,
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 16,
    backgroundColor: 'black'
  },
  title: {
    fontSize: 24,
    textAlign: 'center',
    marginBottom: 16,
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 12,
    paddingHorizontal: 8,
  },
  historyContainer: {
    marginTop: 20,
  },
  historyTitle: {
    fontSize: 18,
    marginBottom: 8,
  },
  historyEntry: {
    fontSize: 16,
  },
  image: {
    width: 100,
    height: 100,
    marginBottom: 8,
    alignSelf: 'center',
  },
});

export default AuthScreen;
