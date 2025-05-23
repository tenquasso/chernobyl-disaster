import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pygame
import sys
from datetime import datetime, timedelta

class ReactorSimulation:
    def __init__(self):
        # physical reactor parameters
        self.thermal_power = 3200e6  # nominal thermal power in watts
        self.coolant_mass = 1500     # coolant mass in kg
        self.volume = 150            # system volume in m³
        self.cooling_efficiency = 0.7 # initial cooling efficiency
        self.fuel_enrichment = 2.0   # uranium enrichment percentage
        self.control_rods = 211      # number of control rods
        self.control_rod_insertion = 0.7  # control rod insertion depth (0-1)
        
        # thermal parameters
        self.temperature = 270       # normal operating temperature in °c
        self.pressure = 7e6          # normal operating pressure in pa
        self.vapor_fraction = 0.2    # normal vapor fraction
        self.steam_quality = 0.0     # steam quality (0-1)
        self.flow_rate = 1000        # coolant flow rate in kg/s
        
        # reactivity parameters
        self.void_coefficient = 4.7  # positive void coefficient (beta)
        self.power_coefficient = -0.1 # power coefficient
        self.xenon_poisoning = 0     # xenon poisoning level
        self.iodine_poisoning = 0    # iodine poisoning level
        self.samarium_poisoning = 0  # samarium poisoning level
        self.reactivity = 0.0        # total reactivity
        
        # safety parameters
        self.max_pressure = 8.8e6    # design pressure limit
        self.max_temperature = 1000  # safe temperature limit
        self.emergency_cooling = True # emergency cooling system status
        self.emergency_power = True  # emergency power system status
        self.containment_integrity = 100 # containment integrity (%)
        
        # radiation parameters
        self.radiation_level = 0.0   # radiation level in sv/h
        self.fission_products = 0.0  # fission product amount
        self.release_rate = 0.0      # radiation release rate
        
        # simulation parameters
        self.time = 0
        self.dt = 0.001             # time step
        self.simulation_speed = 0.1  # simulation speed factor
        self.running = True
        self.explosion_occurred = False
        self.paused = False
        self.simulation_start = datetime.now()
        
        # plotting data
        self.time_data = []
        self.temp_data = []
        self.pressure_data = []
        self.vapor_data = []
        self.power_data = []
        self.xenon_data = []
        self.radiation_data = []
        self.reactivity_data = []
        self.containment_data = []
        
        # initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 800))
        pygame.display.set_caption("chernobyl rbmk reactor simulation")
        
        # initialize fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        
    def calculate_reactivity(self):
        """calculate reactivity based on reactor conditions"""
        # void coefficient effect (positive)
        void_effect = self.void_coefficient * self.vapor_fraction
        
        # power coefficient effect
        power_effect = self.power_coefficient * (self.thermal_power / 3200e6 - 1)
        
        # xenon poisoning effect
        xenon_effect = -0.1 * self.xenon_poisoning
        
        # control rod effect
        control_effect = -0.1 * (1 - self.control_rod_insertion)
        
        # fuel temperature effect
        fuel_temp_effect = -0.0001 * (self.temperature - 270)
        
        self.reactivity = void_effect + power_effect + xenon_effect + control_effect + fuel_temp_effect
        return self.reactivity
    
    def calculate_radiation(self):
        """calculate radiation levels and fission products"""
        # fission product production based on power
        fission_rate = self.thermal_power / 200e6  # mev per fission
        self.fission_products += fission_rate * self.dt * self.simulation_speed
        
        # radiation level calculation
        base_radiation = self.fission_products * 1e-6
        temperature_factor = 1 + (self.temperature - 270) / 1000
        pressure_factor = 1 + (self.pressure - 7e6) / 1e7
        
        self.radiation_level = base_radiation * temperature_factor * pressure_factor
        
        # radiation release rate calculation
        if self.containment_integrity < 100:
            self.release_rate = self.radiation_level * (100 - self.containment_integrity) / 100
        else:
            self.release_rate = 0
    
    def calculate_heat_transfer(self):
        """calculate heat transfer and phase changes"""
        if self.paused:
            return
            
        # reactivity calculation
        reactivity = self.calculate_reactivity()
        
        # thermal power modification based on reactivity
        self.thermal_power *= (1 + reactivity * self.dt * self.simulation_speed)
        
        # heat generated by reactor
        heat_generated = self.thermal_power * self.dt * self.simulation_speed
        
        # emergency cooling system failure simulation
        if self.time > 100 and self.emergency_cooling:
            self.cooling_efficiency = max(0, self.cooling_efficiency - 0.0001)
            if self.cooling_efficiency == 0:
                print("warning: emergency cooling system failure!")
        
        # emergency power system failure simulation
        if self.time > 150 and self.emergency_power:
            self.emergency_power = False
            print("warning: emergency power system failure!")
        
        # heat removed by coolant
        heat_removed = self.cooling_efficiency * heat_generated
        
        # internal energy change
        delta_energy = heat_generated - heat_removed
        
        # temperature change calculation
        specific_heat_water = 4186  # j/kg°c
        specific_heat_vapor = 1996  # j/kg°c
        
        # temperature change based on vapor fraction
        if self.temperature < 100:
            delta_temp = delta_energy / (self.coolant_mass * specific_heat_water)
        else:
            # latent heat of vaporization calculation
            latent_heat = 2257e3  # j/kg
            if delta_energy > 0:
                # water to vapor conversion
                mass_to_vaporize = min(delta_energy / latent_heat, 
                                     self.coolant_mass * (1 - self.vapor_fraction))
                self.vapor_fraction += mass_to_vaporize / self.coolant_mass
                delta_energy -= mass_to_vaporize * latent_heat
            
            # mixed temperature calculation
            delta_temp = delta_energy / (self.coolant_mass * 
                (self.vapor_fraction * specific_heat_vapor + 
                 (1 - self.vapor_fraction) * specific_heat_water))
        
        self.temperature += delta_temp
        
        # pressure calculation using ideal gas equation
        if self.temperature >= 100:
            R = 8.314  # universal gas constant
            vapor_mass = self.coolant_mass * self.vapor_fraction
            self.pressure = (vapor_mass * R * (self.temperature + 273.15)) / self.volume
        
        # steam quality update
        self.steam_quality = min(1.0, self.vapor_fraction * 1.2)
        
        # explosion simulation
        if self.pressure > self.max_pressure * 1.5 or self.temperature > 1000:
            self.explosion_occurred = True
            self.containment_integrity = max(0, self.containment_integrity - 10)
            if self.containment_integrity <= 0:
                self.running = False
                print("accident: reactor explosion occurred!")
                print(f"temperature: {self.temperature:.2f}°c")
                print(f"pressure: {self.pressure/1e6:.2f} mpa")
                print(f"power: {self.thermal_power/1e6:.2f} mw")
                print(f"radiation level: {self.radiation_level:.2f} sv/h")
    
    def update_poisoning(self):
        """update nuclear poison levels"""
        if self.paused:
            return
            
        # xenon-135 production and decay
        xenon_production = 0.1 * self.thermal_power / 3200e6
        xenon_decay = 0.1 * self.xenon_poisoning
        self.xenon_poisoning += (xenon_production - xenon_decay) * self.dt * self.simulation_speed
        
        # iodine-135 production and decay
        iodine_production = 0.05 * self.thermal_power / 3200e6
        iodine_decay = 0.05 * self.iodine_poisoning
        self.iodine_poisoning += (iodine_production - iodine_decay) * self.dt * self.simulation_speed
        
        # samarium-149 production
        samarium_production = 0.01 * self.thermal_power / 3200e6
        self.samarium_poisoning += samarium_production * self.dt * self.simulation_speed
    
    def draw_reactor(self):
        """draw reactor visualization"""
        self.screen.fill((0, 0, 0))
        
        # title
        title = self.title_font.render("chernobyl rbmk reactor simulation", True, (255, 255, 255))
        self.screen.blit(title, (20, 20))
        
        # draw reactor
        reactor_color = (100, 100, 100)
        pygame.draw.rect(self.screen, reactor_color, (400, 200, 400, 400))
        
        # draw temperature indicator
        temp_color = (255, 0, 0) if self.temperature > 300 else (0, 255, 0)
        temp_height = min(400, self.temperature / 2)
        pygame.draw.rect(self.screen, temp_color, 
                        (400, 600 - temp_height, 400, temp_height))
        
        # left panel information
        left_panel = [
            f"temperature: {self.temperature:.1f}°c",
            f"pressure: {self.pressure/1e6:.2f} mpa",
            f"vapor fraction: {self.vapor_fraction:.2f}",
            f"steam quality: {self.steam_quality:.2f}",
            f"power: {self.thermal_power/1e6:.1f} mw",
            f"reactivity: {self.reactivity:.4f}",
            f"control rods: {self.control_rods} ({self.control_rod_insertion*100:.1f}%)",
            f"flow rate: {self.flow_rate:.1f} kg/s"
        ]
        
        # right panel information
        right_panel = [
            f"xenon: {self.xenon_poisoning:.2f}",
            f"iodine: {self.iodine_poisoning:.2f}",
            f"samarium: {self.samarium_poisoning:.2f}",
            f"radiation level: {self.radiation_level:.2f} sv/h",
            f"radiation release: {self.release_rate:.2f} sv/h",
            f"containment integrity: {self.containment_integrity:.1f}%",
            f"fission products: {self.fission_products:.2e}"
        ]
        
        # system status
        status_panel = [
            f"status: {'paused' if self.paused else 'running'}",
            f"speed: {self.simulation_speed:.1f}x",
            f"time: {self.time:.1f} s",
            f"cooling system: {'active' if self.cooling_efficiency > 0 else 'failed'}",
            f"power system: {'active' if self.emergency_power else 'failed'}"
        ]
        
        # display information panels
        for i, text in enumerate(left_panel):
            text_render = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_render, (20, 100 + i * 40))
            
        for i, text in enumerate(right_panel):
            text_render = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_render, (900, 100 + i * 40))
            
        for i, text in enumerate(status_panel):
            color = (255, 165, 0) if "failed" in text else (0, 255, 0) if "active" in text else (255, 255, 255)
            text_render = self.font.render(text, True, color)
            self.screen.blit(text_render, (20, 700 + i * 30))
        
        # control instructions
        controls = [
            "controls:",
            "space - pause/resume",
            "up/down - speed",
            "esc - exit"
        ]
        for i, text in enumerate(controls):
            control_text = self.small_font.render(text, True, (200, 200, 200))
            self.screen.blit(control_text, (900, 700 + i * 25))
        
        pygame.display.flip()
    
    def run(self):
        """run simulation"""
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_UP:
                        self.simulation_speed = min(2.0, self.simulation_speed + 0.1)
                    elif event.key == pygame.K_DOWN:
                        self.simulation_speed = max(0.1, self.simulation_speed - 0.1)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # update simulation
            self.calculate_heat_transfer()
            self.update_poisoning()
            self.calculate_radiation()
            self.update_plot()
            self.draw_reactor()
            
            self.time += self.dt
            clock.tick(30)  # 30 fps
        
        pygame.quit()
        
        # plot results after simulation ends
        self.plot_results()
    
    def update_plot(self):
        """update plotting data"""
        self.time_data.append(self.time)
        self.temp_data.append(self.temperature)
        self.pressure_data.append(self.pressure/1e6)
        self.vapor_data.append(self.vapor_fraction)
        self.power_data.append(self.thermal_power/1e6)
        self.xenon_data.append(self.xenon_poisoning)
        self.radiation_data.append(self.radiation_level)
        self.reactivity_data.append(self.reactivity)
        self.containment_data.append(self.containment_integrity)
    
    def plot_results(self):
        """create simulation results graphs"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        ax1.plot(self.time_data, self.temp_data, 'r-', label='temperature')
        ax1.plot(self.time_data, self.pressure_data, 'b-', label='pressure')
        ax1.set_ylabel('temperature (°c) / pressure (mpa)')
        ax1.grid(True)
        ax1.legend()
        
        ax2.plot(self.time_data, self.power_data, 'g-', label='power')
        ax2.plot(self.time_data, self.reactivity_data, 'y-', label='reactivity')
        ax2.set_ylabel('power (mw) / reactivity')
        ax2.grid(True)
        ax2.legend()
        
        ax3.plot(self.time_data, self.radiation_data, 'r-', label='radiation')
        ax3.plot(self.time_data, self.containment_data, 'b-', label='containment')
        ax3.set_xlabel('time (s)')
        ax3.set_ylabel('radiation level (sv/h) / integrity (%)')
        ax3.grid(True)
        ax3.legend()
        
        ax4.plot(self.time_data, self.xenon_data, 'g-', label='xenon')
        ax4.plot(self.time_data, self.vapor_data, 'y-', label='vapor fraction')
        ax4.set_xlabel('time (s)')
        ax4.set_ylabel('xenon level / vapor fraction')
        ax4.grid(True)
        ax4.legend()
        
        plt.suptitle('chernobyl accident simulation', fontsize=16)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    simulation = ReactorSimulation()
    simulation.run() 