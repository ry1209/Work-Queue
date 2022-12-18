from dataclasses import dataclass
from typing import Optional
from Config import config
from RPA.Browser.Selenium import Selenium

class GoActionsElements:
    PLAYER_INFO_BUTTON = lambda x: fr'xpath://html/body/table[2]/tbody/tr[{str(x+1)}]/td[2]/a'
    PLAYER_NAME = lambda x: fr'xpath://html/body/table[2]/tbody/tr[{str(x+1)}]/td[2]/a'
    NUMBER_OF_WINS = r'xpath://html/body/table[1]/tbody/tr[1]/td'
    TOTAL_GAMES_PLAYED = r'xpath://html/body/table[1]/tbody/tr[3]/td'

@dataclass
class GoBase:
    
    headless: Optional[bool] = False

    def __post_init__(self):
        self.go_url = config['GO']['go_rating_webpage']
        self.driver = Selenium()
        self.driver.set_selenium_implicit_wait(25)
    
    def launch(self) -> None:
        if self.headless:
            self.driver.open_headless_chrome_browser(self.go_url)
        else:
            self.driver.open_available_browser(self.go_url)
        self.driver.maximize_browser_window()
    
    def get_player_name(self, player_rank : int) -> str:
        return self.driver.find_element(GoActionsElements.PLAYER_NAME(player_rank)).text
    
    def tear_down(self) -> None:
        self.driver.close_browser()

@dataclass
class GoActions(GoBase):

    def get_player_win_rate(self, player_rank : int) -> int:
        self.driver.click_element_when_visible(GoActionsElements.PLAYER_INFO_BUTTON(player_rank))
        wins = int(self.driver.find_element(GoActionsElements.NUMBER_OF_WINS).text)
        total_games = int(self.driver.find_element(GoActionsElements.TOTAL_GAMES_PLAYED).text)
        return round(wins/total_games,2)