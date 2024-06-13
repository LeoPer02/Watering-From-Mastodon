import React, { Component } from 'react';
import { View, Text, StyleSheet, FlatList, ActivityIndicator, Button, Alert, Modal, TouchableOpacity, TextInput, Image } from 'react-native';
import { accountService } from '../_services/account';
import Toast from 'react-native-toast-message';

class Dashboard extends Component {
  constructor(props) {
    super(props);

    this.reloadPlants = this.reloadPlants.bind(this);
    this.changeThresholds = this.changeThresholds.bind(this);

    this.state = {
      plants: [],
      loading: false,
      showModal: false,
      selectedPlant: null,
      control_agent_name: '',
      control_agent_ip: '',
      control_agent_port: '',
      showAddModal: false,
      showThresholdModal: false,
      showPoolModal: false,
      poolData: [],
      expandedPlantIds: [],
      waterLower: 0,
      waterUpper: 0,
      heatLower: 0,
      heatUpper: 0,
      lightLower: 0,
      lightUpper: 0,
      humidityUpper: 0,
      humidityLower: 0,
    };
  }

  reloadPlants = async () => {
    const plants = await accountService.control_agents();
    this.setState({ plants: plants, loading: false });
  };

  async componentDidMount() {
    try {
      this.setState({ loading: true });
      const plants = await accountService.control_agents();
      this.setState({ plants: plants, loading: false });
    } catch (error) {
      console.error(error);
      this.setState({ loading: false });
    }
  }

  handleSendCommand = async (id, command) => {
    try {
      await accountService.action(id, command);
      Toast.show({
        type: 'success',
        text1: 'Command sent successfully',
      });
      this.reloadPlants();
    } catch (error) {
      Toast.show({
        type: 'error',
        text1: 'Failed to send command',
      });
    }
  };

  handleRemovePlant = async () => {
    const { selectedPlant } = this.state;
    if (selectedPlant) {
      try {
        await accountService.remove_ca(selectedPlant.ip, selectedPlant.port);
        this.setState((prevState) => ({
          plants: prevState.plants.filter(plant => plant.id !== selectedPlant.id),
          showModal: false,
          selectedPlant: null,
        }));
        Toast.show({
          type: 'success',
          text1: 'Plant removed successfully',
        });
      } catch (error) {
        Toast.show({
          type: 'error',
          text1: 'Failed to remove plant',
        });
      }
    }
  };

  handleAddPlant = async () => {
    const { control_agent_name, control_agent_ip, control_agent_port } = this.state;
    try {
      const newPlant = await accountService.add_ca(control_agent_name, control_agent_ip, control_agent_port);
      this.setState((prevState) => ({
        plants: [...prevState.plants, newPlant],
        showAddModal: false,
        control_agent_name: '',
        control_agent_ip: '',
        control_agent_port: ''
      }));
      Toast.show({
        type: 'success',
        text1: 'Plant added successfully',
      });
      const plants = await accountService.control_agents();
      this.setState({ plants: plants, loading: false });
    } catch (error) {
      Toast.show({
        type: 'error',
        text1: 'Failed to add plant',
      });
    }
  };

  changeThresholds = async () => {
    const { selectedPlant, waterLower, waterUpper, heatLower, heatUpper, lightLower, lightUpper, humidityUpper, humidityLower } = this.state;

    data = {
      control_agent: selectedPlant.id,
      light_value_low: lightLower,
      light_value_high: lightUpper,
      moisture_value_high: waterUpper,
      moisture_value_low: waterLower,
      temperature_value_low: heatLower,
      temperature_value_high: heatUpper,
      humidity_value_low: humidityLower,
      humidity_value_high: humidityUpper
    };
    try {
      const plants = await accountService.set_thresholds(data);
      Toast.show({
        type: 'success',
        text1: 'Thresholds updated successfully',
      });
      this.reloadPlants();
      this.closeThresholdModal();
    } catch (error) {
      Toast.show({
        type: 'error',
        text1: 'Failed to update thresholds',
      });
    }
  };

  fetchPoolData = async (plant) => {
    try {
      const pools = await accountService.pool();
      const selectedPlantPool = pools.find(p => p.id === plant.id);
      this.setState({ poolData: selectedPlantPool.pool, showPoolModal: true, selectedPlant: plant });
    } catch (error) {
      Toast.show({
        type: 'error',
        text1: 'Failed to fetch pool data',
      });
    }
  };

  openModal = (plant) => {
    this.setState({ showModal: true, selectedPlant: plant });
  };

  closeModal = () => {
    this.setState({ showModal: false, selectedPlant: null });
  };

  openAddModal = () => {
    this.setState({ showAddModal: true });
  };

  closeAddModal = () => {
    this.setState({ showAddModal: false });
  };

  openThresholdModal = async (plant) => {
    await accountService.get_threshold(plant.id).then((response) => {
      this.setState({
        waterLower: response[0].threshold.moisture_value_low,
        waterUpper: response[0].threshold.moisture_value_high,
        heatLower: response[0].threshold.temperature_value_low,
        heatUpper: response[0].threshold.temperature_value_high,
        lightLower: response[0].threshold.light_value_low,
        lightUpper: response[0].threshold.light_value_high,
        humidityUpper: response[0].threshold.humidity_value_low,
        humidityLower: response[0].threshold.humidity_value_high,
      });
    });
    this.setState({ showThresholdModal: true, selectedPlant: plant });
  };

  closeThresholdModal = () => {
    this.setState({ showThresholdModal: false });
  };

  closePoolModal = () => {
    this.setState({ showPoolModal: false, poolData: [] });
  };

  toggleExpand = (plantId) => {
    this.setState((prevState) => {
      const { expandedPlantIds } = prevState;
      if (expandedPlantIds.includes(plantId)) {
        return { expandedPlantIds: expandedPlantIds.filter(id => id !== plantId) };
      } else {
        return { expandedPlantIds: [...expandedPlantIds, plantId] };
      }
    });
  };

  renderCard = ({ item }) => {
    const { expandedPlantIds } = this.state;
    const isExpanded = expandedPlantIds.includes(item.id);
  
    return (
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>{item.name}</Text>
          <View style={styles.buttonGroup}>
            <TouchableOpacity style={styles.infoButton} onPress={() => this.fetchPoolData(item)}>
              <Text style={styles.infoButtonText}>I</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.closeButton} onPress={() => this.openModal(item)}>
              <Text style={styles.closeButtonText}>X</Text>
            </TouchableOpacity>
          </View>
        </View>
        <Text style={styles.text}>{item.ip}:{item.port}</Text>
        <View style={styles.buttonContainer}>
          <Button
            title="Water"
            onPress={() => {
              this.handleSendCommand(item.id, 'water');
            }}
          />
          <Button
            title="Heat"
            onPress={() => this.handleSendCommand(item.id, 'heat')}
          />
          <Button
            title="Light"
            onPress={() => this.handleSendCommand(item.id, 'light')}
          />
          <Button
            title="Thresholds"
            onPress={() => this.openThresholdModal(item)}
          />
        </View>
        <TouchableOpacity onPress={() => this.toggleExpand(item.id)} style={styles.expandButton}>
          <Text style={styles.expandButtonText}>{isExpanded ? 'Hide Logs' : 'Show Logs'}</Text>
        </TouchableOpacity>
        {isExpanded && (
          <View style={styles.logsContainer}>
            {item.commands && item.commands.length > 0 ? (
              <FlatList
                data={[...item.commands].reverse()}
                renderItem={({ item }) => {
                  const createdDate = new Date(item.created_date);
                  const year = createdDate.getFullYear();
                  const month = String(createdDate.getMonth() + 1).padStart(2, '0');
                  const day = String(createdDate.getDate()).padStart(2, '0');
                  const hours = String(createdDate.getHours()).padStart(2, '0');
                  const minutes = String(createdDate.getMinutes()).padStart(2, '0');
                  const formattedDate = `${year}-${month}-${day} ${hours}-${minutes}`;
  
                  const command = item.command.charAt(0).toUpperCase() + item.command.slice(1);
                  return (
                    <Text style={styles.logText}>
                      [{formattedDate}] Action- {command}
                    </Text>
                  );
                }}
                keyExtractor={(item, index) => index.toString()}
              />
            ) : (
              <Text style={styles.logText}>No logs available</Text>
            )}
          </View>
        )}
      </View>
    );
  };
  
  formatDate = (dateString) => {
    const createdDate = new Date(dateString);
    const year = createdDate.getFullYear();
    const month = String(createdDate.getMonth() + 1).padStart(2, '0');
    const day = String(createdDate.getDate()).padStart(2, '0');
    const hours = String(createdDate.getHours()).padStart(2, '0');
    const minutes = String(createdDate.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  }

  handleInputChange = (field, value) => {
    this.setState({ [field]: value });
  };

  render() {
    const { plants, loading, showModal, showAddModal, showThresholdModal, showPoolModal, poolData, control_agent_name, control_agent_ip, control_agent_port, waterLower, waterUpper, heatLower, heatUpper, lightLower, lightUpper, humidityLower, humidityUpper } = this.state;

    if (loading) {
      return (
        <View style={styles.loader}>
          <ActivityIndicator size="large" color="#0000ff" />
        </View>
      );
    }

    return (
      <View style={styles.container}>
        {plants && plants.length > 0 ? (
          <FlatList
            data={plants}
            renderItem={this.renderCard}
            keyExtractor={(item) => item.id}
            contentContainerStyle={styles.list}
          />
        ) : (
          <Text style={styles.title}>There are no plants available. Try adding one!</Text>
        )}

        <Modal
          transparent={true}
          visible={showModal}
          onRequestClose={this.closeModal}
        >
          <View style={styles.modalBackground}>
            <View style={styles.modalContainer}>
              <Text style={styles.modalText}>Confirm you want to remove the plant?</Text>
              <View style={styles.modalButtonContainer}>
                <Button title="Confirm" onPress={this.handleRemovePlant} />
                <Button title="Cancel" onPress={this.closeModal} />
              </View>
            </View>
          </View>
        </Modal>

        <Modal
          transparent={true}
          visible={showAddModal}
          onRequestClose={this.closeAddModal}
        >
          <View style={styles.modalBackground}>
            <View style={styles.modalContainer}>
              <Text style={styles.modalText}>Add a new plant</Text>
              <TextInput
                style={styles.input}
                placeholder="Plant name"
                value={control_agent_name}
                autoCapitalize="none"
                placeholderTextColor="black"
                onChangeText={(value) => this.handleInputChange('control_agent_name', value)}
              />
              <TextInput
                style={styles.input}
                placeholder="IP"
                value={control_agent_ip}
                autoCapitalize="none"
                placeholderTextColor="black"
                onChangeText={(value) => this.handleInputChange('control_agent_ip', value)}
              />
              <TextInput
                style={styles.input}
                placeholder="Port"
                value={control_agent_port}
                autoCapitalize="none"
                placeholderTextColor="black"
                onChangeText={(value) => this.handleInputChange('control_agent_port', value)}
              />
              <View style={styles.modalButtonContainer}>
                <Button title="Add" onPress={this.handleAddPlant} />
                <Button title="Cancel" onPress={this.closeAddModal} />
              </View>
            </View>
          </View>
        </Modal>

        <Modal
          transparent={true}
          visible={showThresholdModal}
          onRequestClose={this.closeThresholdModal}
        >
          <View style={styles.modalBackground}>
            <View style={styles.modalContainer}>
              <Text style={styles.modalText}>Set Thresholds</Text>
              
              <Text style={styles.inputLabel}>Water Lower</Text>
              <TextInput
                style={styles.input}
                value={waterLower.toString()}
                keyboardType="numeric"
                placeholderTextColor="black"
                onChangeText={(value) => {
                  const numericValue = Math.max(0, Math.min(500, Number(value)));
                  this.handleInputChange('waterLower', numericValue.toString());
                }}
              />
              
              <Text style={styles.inputLabel}>Water Upper</Text>
              <TextInput
                style={styles.input}
                value={waterUpper.toString()}
                keyboardType="numeric"
                placeholderTextColor="black"
                onChangeText={(value) => {
                  const numericValue = Math.max(0, Math.min(500, Number(value)));
                  this.handleInputChange('waterUpper', numericValue.toString());
                }}
              />
              
              <Text style={styles.inputLabel}>Heat Lower</Text>
              <TextInput
                style={styles.input}
                value={heatLower.toString()}
                keyboardType="numeric"
                placeholderTextColor="black"
                onChangeText={(value) => {
                  const numericValue = Math.max(0, Math.min(500, Number(value)));
                  this.handleInputChange('heatLower', numericValue.toString());
                }}
              />
              
              <Text style={styles.inputLabel}>Heat Upper</Text>
              <TextInput
                style={styles.input}
                value={heatUpper.toString()}
                keyboardType="numeric"
                placeholderTextColor="black"
                onChangeText={(value) => {
                  const numericValue = Math.max(0, Math.min(500, Number(value)));
                  this.handleInputChange('heatUpper', numericValue.toString());
                }}
              />
              
              <Text style={styles.inputLabel}>Light Lower</Text>
              <TextInput
                style={styles.input}
                value={lightLower.toString()}
                keyboardType="numeric"
                placeholderTextColor="black"
                onChangeText={(value) => {
                  const numericValue = Math.max(0, Math.min(500, Number(value)));
                  this.handleInputChange('lightLower', numericValue.toString());
                }}
              />
              
              <Text style={styles.inputLabel}>Light Upper</Text>
              <TextInput
                style={styles.input}
                value={lightUpper.toString()}
                keyboardType="numeric"
                placeholderTextColor="black"
                onChangeText={(value) => {
                  const numericValue = Math.max(0, Math.min(500, Number(value)));
                  this.handleInputChange('lightUpper', numericValue.toString());
                }}
              />
              
              <Text style={styles.inputLabel}>Humidity Lower</Text>
              <TextInput
                style={styles.input}
                value={humidityLower.toString()}
                keyboardType="numeric"
                placeholderTextColor="black"
                onChangeText={(value) => {
                  const numericValue = Math.max(0, Math.min(500, Number(value)));
                  this.handleInputChange('humidityLower', numericValue.toString());
                }}
              />
              
              <Text style={styles.inputLabel}>Humidity Upper</Text>
              <TextInput
                style={styles.input}
                value={humidityUpper.toString()}
                keyboardType="numeric"
                placeholderTextColor="black"
                onChangeText={(value) => {
                  const numericValue = Math.max(0, Math.min(500, Number(value)));
                  this.handleInputChange('humidityUpper', numericValue.toString());
                }}
              />

              <View style={styles.modalButtonContainer}>
                <Button title="Confirm" onPress={this.changeThresholds} />
                <Button title="Cancel" onPress={this.closeThresholdModal} />
              </View>
            </View>
          </View>
        </Modal>

        <Modal
          transparent={true}
          visible={showPoolModal}
          onRequestClose={this.closePoolModal}
        >
          <View style={styles.modalBackground}>
            <View style={styles.modalContainer}>
              <Text style={styles.modalText}>Current values: {this.state.selectedPlant && this.state.selectedPlant.name}</Text>
              <FlatList
                data={poolData}
                renderItem={({ item }) => (
                  <View style={styles.poolItem}>
                    <Text style={styles.poolDate}>{this.formatDate(item.date)}</Text>
                    <Text style={styles.poolText}>Humidity: {item.humidity_value}</Text>
                    <Text style={styles.poolText}>Light: {item.light_value}</Text>
                    <Text style={styles.poolText}>Moisture: {item.moisture_value}</Text>
                    <Text style={styles.poolText}>Temperature: {item.temperature_value}</Text>
                  </View>
                )}
                keyExtractor={(item) => item.id.toString()}
              />
              <Button title="Close" onPress={this.closePoolModal} />
            </View>
          </View>
        </Modal>

        <Button
          title="Add Plant"
          onPress={this.openAddModal}
        />
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  loader: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  list: {
    paddingBottom: 16,
  },
  card: {
    backgroundColor: '#fff',
    padding: 16,
    marginBottom: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 2,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  buttonGroup: {
    flexDirection: 'row',
  },
  infoButton: {
    backgroundColor: 'blue',
    borderRadius: 50,
    width: 30,
    height: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  infoButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  closeButton: {
    backgroundColor: 'red',
    borderRadius: 50,
    width: 30,
    height: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
    color: 'black',
  },
  text: {
    color: 'black',
  },
  expandButton: {
    marginTop: 8,
    alignItems: 'center',
  },
  expandButtonText: {
    color: 'blue',
    textDecorationLine: 'underline',
  },
  logsContainer: {
    marginTop: 8,
    backgroundColor: '#f0f0f0',
    padding: 8,
    borderRadius: 8,
  },
  logText: {
    color: 'black',
  },
  modalBackground: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContainer: {
    width: '90%',
    maxHeight: '90%',
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
    alignItems: 'center',
  },
  modalText: {
    fontSize: 16,
    marginBottom: 16,
    color: 'black',
  },
  modalButtonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
  },
  title: {
    color: 'black',
    marginTop: 20,
    marginLeft: 0,
    marginRight: 50,
    fontSize: 24,
    lineHeight: 54,
    marginBottom: 20,
    fontWeight: 'bold',
  },
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 12,
    width: '100%',
    paddingHorizontal: 8,
    color: 'black',
  },
  inputLabel: {
    fontSize: 16,
    color: 'black',
    marginBottom: 4,
  },
  poolItem: {
    marginBottom: 10,
  },
  poolDate: {
    fontWeight: 'bold',
    color: 'black',
  },
  poolText: {
    color: 'black',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
});



export default Dashboard;