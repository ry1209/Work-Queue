from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple
from abc import ABC, abstractmethod
from web_automation.go_frontend import GoActions
from web_automation.go_backend import GoWeb

class State(Enum):
    """Work item state."""

    DONE = "COMPLETED"
    FAILED = "FAILED"

class Error(Enum):
    """Failed work item error type."""

    BUSINESS = "BUSINESS"  
    APPLICATION = "APPLICATION" 

@dataclass
class WorkItem:
    id : int
    payload : Optional[dict] = field(default_factory=dict)
    item_status : dict = field(
        default_factory= lambda: {
            'state' : None,
            'exception_type' : None,
            'exception_message' : ''
        }
    )

class ProcessingMethod(ABC):
    '''
    ProcessingMethod abstract base class, users should create their own processing method by 
    following this template
    '''
    def grab_input_item_data(self, item) -> Tuple[int,dict]:
        return item.id, item.payload

    @abstractmethod
    def create_payload(self) -> List[dict]:
        raise NotImplementedError

    @abstractmethod
    def process_work_item(self, item) -> Tuple[int,dict]:
        raise NotImplementedError

class DefaultProcessingMethod(ProcessingMethod):
    '''
    Default processing method: simply outputs numbers from 1 to 10 to the work item payload
    '''
    def create_payload(self) -> List[dict]:
        payload = []
        for i in range(1,10):
            payload.append(
                    {
                        i : i
                    }
                )
        return payload
    def process_work_item(self, item : WorkItem) -> None:
        if item.id % 2 == 0:
            raise Exception('Trigger exception on purpose.')
        return item.id, {'data':item.id}

class GoScraperBackendProcessingMethod(ProcessingMethod):
    '''
    Default processing method:  A website scraper for go rankings using a simple HTTP GET request
    '''
    def create_payload(self) -> List[dict]: 
        payload = []
        # grab top 50 players
        for i in range(1,51):
            payload.append(
                    {
                        'Rank' : i
                    }
                )
        return payload
    def process_work_item(self, item : WorkItem) -> Tuple[int,dict]:
        go_web = GoWeb() 
        id,input = self.grab_input_item_data(item)
        player_rank = input['Rank']
        return id, {
            'Name' : go_web.get_player_name_by_rank(player_rank),
            'Elo' : go_web.get_player_elo_by_rank(player_rank)
        }

class GoScraperFrontendProcessingMethod(ProcessingMethod):
    '''
    Default processing method:  A website scraper for go rankings leveraging Selenium UI automation
    '''
    def create_payload(self) -> List[dict]: 
        payload = []
        # grab top 10 players 
        for i in range(1,11):
            payload.append(
                    {
                        'Rank' : i
                    }
                )
        return payload
    def process_work_item(self, item : WorkItem) -> Tuple[int,dict]:
        go_actions = GoActions() 
        id,input = self.grab_input_item_data(item)
        player_rank = input['Rank']
        try:
            go_actions.launch()
            player_name = go_actions.get_player_name(player_rank)
            player_win_rate = go_actions.get_player_win_rate(player_rank)
        except Exception as e:
            raise Exception(e)
        finally:
            go_actions.tear_down()
        return id, {
            'Name' : player_name,
            'Winrate' : player_win_rate
        }