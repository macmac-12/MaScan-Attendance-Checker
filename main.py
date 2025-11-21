"""Weather Application using Flet v0.28.3 - Responsive Design"""

import flet as ft

from weather_service import WeatherService, WeatherServiceError, CityNotFoundError, NetworkError
from config import Config

# 1. DEFINE MAPPING for Colors and Emojis/Icons
WEATHER_MAPPING = {
    "2": {"color": ft.colors.DEEP_PURPLE_800, "icon": "⛈️"},
    "3": {"color": ft.colors.BLUE_GREY_700, "icon": "🌧️"},
    "5": {"color": ft.colors.INDIGO_600, "icon": "☔"},
    "6": {"color": ft.colors.LIGHT_BLUE_200, "icon": "❄️"},
    "7": {"color": ft.colors.BLUE_GREY_400, "icon": "🌫️"},
    "800": {"color": ft.colors.YELLOW_400, "icon": "☀️"},
    "8": {"color": ft.colors.BLUE_GREY_300, "icon": "☁️"},
    "default": {"color": ft.colors.WHITE, "icon": "❓"},
}

# 2. ALERT CRITERIA DEFINITION
ALERT_THRESHOLDS = {
    "HEAT": {"temp": 35.0, "color": ft.colors.RED_700, "recommendation": "🔥 EXTREME HEAT WARNING! Stay hydrated and limit outdoor activity."},
    "COLD": {"temp": 5.0, "color": ft.colors.BLUE_700, "recommendation": "🥶 COLD WARNING! Wear warm layers and protect exposed skin."},
    "RAIN": {"group_id_prefix": '5', "color": ft.colors.ORANGE_700, "recommendation": "🌧️ Heavy Rain Expected. Bring an umbrella and drive safely."},
    "SUN": {"uv_temp": 28.0, "color": ft.colors.YELLOW_800, "recommendation": "☀️ High UV Index expected. Wear sunscreen and a hat."},
}


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.setup_page()
        self.build_ui()
    
    def setup_page(self):
        """Configure page settings and set up color transition."""
        self.page.title = Config.APP_TITLE
        
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        
        self.page.bgcolor = ft.colors.WHITE
        self.page.animate_bgcolor = 300
    
        self.page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)
        self.page.dark_theme = ft.Theme(
            color_scheme_seed=ft.colors.BLUE,
            color_scheme=ft.ColorScheme(background=ft.colors.BLACK87), 
        )
    
        self.page.padding = 20
        
        # Set initial size, but remove fixed enforcement
        self.page.window_width = 900
        self.page.window_height = 1080 
        self.page.window_center()
        
        self.page.window_resizable = True 
        
    
    def build_ui(self):
        """Build the user interface."""
        
        self.title = ft.Text("Weather App", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_700)
        
        self.theme_button = ft.IconButton(
            icon=ft.icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )

        title_row = ft.Row(
            [self.title, self.theme_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.colors.BLUE_400,
            prefix_icon=ft.icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
            expand=True,
        )
        
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.BLUE_700),
        )

        input_row = ft.Row(
            [
                self.city_input,
                self.search_button,
            ],
            spacing=10
        )

        self.custom_icon_display = ft.Text("🔎", size=80)

        self.alert_banner = ft.Container(
            content=ft.Text("", color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
            padding=10,
            margin=ft.margin.only(top=10, bottom=10),
            border_radius=5,
            visible=False,
            alignment=ft.alignment.center,
            expand=True 
        )

        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.SURFACE), 
            border_radius=10,
            padding=20,
            expand=True 
        )
        
        self.error_message = ft.Text("", color=ft.colors.RED_700, visible=False)
        self.loading = ft.ProgressRing(visible=False)
        
        # Main content column
        self.main_content = ft.Column(
            [
                title_row,
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                
                input_row, 
                
                ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                self.loading,
                self.error_message,
                self.alert_banner,
                self.custom_icon_display,
                self.weather_container,
                ft.Container(expand=True), 
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            expand=True, 
        )
        
        self.page.add(self.main_content)
    
    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.icons.DARK_MODE
        self.page.update()
    
    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)
    
    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        if not city:
            self.show_error("Please enter a city name.")
            return
        
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.alert_banner.visible = False 
        self.page.update()
        
        try:
            weather_data = await self.weather_service.get_weather(city)
            self.display_weather(weather_data)
        
        except WeatherServiceError as e:
            self.show_error(str(e))
        
        except Exception as e:
            self.show_error("An unexpected error occurred. Please try again.")
        
        finally:
            self.loading.visible = False
            self.page.update()
            
    
    def check_alerts(self, temp: float, weather_id: str) -> dict or None:
        """Checks temperature and weather ID against defined alert thresholds."""
        
        if temp >= ALERT_THRESHOLDS["HEAT"]["temp"]:
            return ALERT_THRESHOLDS["HEAT"]
        
        if temp <= ALERT_THRESHOLDS["COLD"]["temp"]:
            return ALERT_THRESHOLDS["COLD"]
            
        if weather_id.startswith(ALERT_THRESHOLDS["RAIN"]["group_id_prefix"]) or weather_id.startswith('2'):
            return ALERT_THRESHOLDS["RAIN"]
            
        if temp >= ALERT_THRESHOLDS["SUN"]["uv_temp"] and not weather_id.startswith(('6', '2', '5')): 
             return ALERT_THRESHOLDS["SUN"]
             
        return None

    def display_weather(self, data: dict):
        """Display weather information and animate the reveal, including background color change."""
        
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        
        weather_id = str(data.get("weather", [{}])[0].get("id", "0"))
        
        if weather_id == "800":
            mapping = WEATHER_MAPPING["800"]
        else:
            category_key = weather_id[0] if weather_id else "default"
            mapping = WEATHER_MAPPING.get(category_key, WEATHER_MAPPING["default"])

        new_bgcolor = mapping["color"]
        custom_icon = mapping["icon"]
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        alert = self.check_alerts(temp, weather_id)
        
        if alert:
            self.alert_banner.content.value = alert["recommendation"]
            self.alert_banner.bgcolor = alert["color"]
            self.alert_banner.visible = True
        else:
            self.alert_banner.visible = False

        self.custom_icon_display.value = custom_icon
        self.page.bgcolor = new_bgcolor
        
        self.weather_container.content = ft.Column(
            [
                ft.Text(f"{city_name}, {country}", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(description, size=20, italic=True),
                ft.Text(
                    f"{temp:.1f}°C",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_900,
                ),
                ft.Text(
                    f"Feels like {feels_like:.1f}°C",
                    size=16,
                    color=ft.colors.with_opacity(0.8, ft.colors.ON_BACKGROUND), 
                ),
                ft.Divider(),
                ft.Row(
                    [
                        self.create_info_card(ft.icons.WATER_DROP, "Humidity", f"{humidity}%"),
                        self.create_info_card(ft.icons.AIR, "Wind Speed", f"{wind_speed} m/s"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        
        self.page.update() 
        
        self.weather_container.opacity = 1
        self.error_message.visible = False
        self.page.update()
    
    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.colors.BLUE_700),
                    ft.Text(label, size=12, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE)), 
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE_900,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.colors.SURFACE_VARIANT, 
            border_radius=10,
            padding=15,
            # FIX 5: Remove fixed width and allow card to expand horizontally
            expand=True,
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.alert_banner.visible = False
        self.page.bgcolor = ft.colors.WHITE
        self.page.update()


def main(page: ft.Page):
    """Main entry point for the Flet application."""
    WeatherApp(page)

# =========================================================================
# MAIN EXECUTION BLOCK
# =========================================================================

if __name__ == "__main__":
    ft.app(target=main)