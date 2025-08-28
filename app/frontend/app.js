const { createApp } = Vue;

createApp({
    data() {
        return {
            dutyCycle: 63.27,
            testDuration: 10,
            thrusterRunning: false,
            testRunning: false,
            powerConnected: false,
            forceConnected: false,
            sensorData: {
                rpm: 0,
                voltage: 0.0,
                current: 0.0,
                force: 0.0
            },
            testResults: null,
            updateInterval: null
        }
    },
    mounted() {
        this.startDataUpdates();
    },
    methods: {
        async apiCall(endpoint, method = 'GET', data = null) {
            try {
                const options = {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                    }
                };
                
                if (data) {
                    options.data = data;
                }
                
                const response = await axios({
                    method: method,
                    url: endpoint,
                    data: data,
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                return response.data;
            } catch (error) {
                console.error('API Error:', error);
                return { status: 'error', message: error.response?.data?.message || error.message };
            }
        },

        async startThruster() {
            const dutyCycle = parseFloat(this.dutyCycle) / 100;
            const result = await this.apiCall('/thruster/start', 'POST', { duty_cycle: dutyCycle });
            
            if (result.status === 'success') {
                this.thrusterRunning = true;
                this.showAlert('Thruster started successfully!', 'success');
            } else {
                this.showAlert('Failed to start thruster: ' + result.message, 'danger');
            }
        },

        async stopThruster() {
            const result = await this.apiCall('/thruster/stop', 'POST');
            
            if (result.status === 'success') {
                this.thrusterRunning = false;
                this.showAlert('Thruster stopped successfully!', 'success');
            } else {
                this.showAlert('Failed to stop thruster: ' + result.message, 'danger');
            }
        },

        async startTest() {
            if (this.testRunning) {
                this.showAlert('Test already running!', 'warning');
                return;
            }

            this.testRunning = true;
            
            const result = await this.apiCall('/tests/start', 'POST', { 
                duration: this.testDuration, 
                duty_cycle: parseFloat(this.dutyCycle) / 100 
            });
            
            if (result.status === 'success') {
                this.showAlert(`Test completed! Collected ${result.data_points} data points.`, 'success');
                this.testResults = result;
            } else {
                this.showAlert('Test failed: ' + result.message, 'danger');
            }
            
            this.testRunning = false;
        },

        startDataUpdates() {
            this.updateInterval = setInterval(async () => {
                await this.updateSensorData();
            }, 1000);
        },

        async updateSensorData() {
            // Update RPM
            const rpmData = await this.apiCall('/sensors/rpm');
            if (rpmData.status === 'success') {
                this.sensorData.rpm = rpmData.rpm;
            }

            // Update power
            const powerData = await this.apiCall('/sensors/power');
            if (powerData.status === 'success') {
                this.sensorData.voltage = powerData.voltage;
                this.sensorData.current = powerData.current;
                this.powerConnected = powerData.voltage > 0;
            } else {
                this.powerConnected = false;
            }

            // Update force
            const forceData = await this.apiCall('/sensors/force');
            if (forceData.status === 'success' && forceData.force !== null) {
                this.sensorData.force = forceData.force;
                this.forceConnected = true;
            } else {
                this.forceConnected = false;
            }
        },

        showAlert(message, type) {
            // Create alert element
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.querySelector('.container-fluid').insertBefore(alertDiv, document.querySelector('.row'));
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    },
    beforeUnmount() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}).mount('#app');
