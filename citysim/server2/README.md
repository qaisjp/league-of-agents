# SmartCity REST API

In this challenge, you will need to operate cars in a city to deliver customers. Your goal is to operate the cars to more customers with less ecological footprint and at the same time provide good service to the customers.
* Ecological footprint is evaluated by the time of your cars on travel.
* Quality of Service to the customers is evaluated by the sum of the time that the customers wait to be picked and the time that they are on travel.

The operations are done by sending HTTP requests to a server. The server runs the SmartCity simulation. During the simulation, you can operate the server and simulation objects by requesting server REST APIs.

The APIs for SmartCity challenge are listed below.

## Admin APIs
Admin APIs are used to add teams or start/stop the simulation. Admin APIs requires team key <TEAM_KEY> to access (given by mentors). The key shall not be shared with others.
 * https://api.citysimulation.eu/<TEAM_KEY>
   * Method: Any
   * Descriptions: This API provides an HTML page with information about teams on the simulation server and their access tokens <YOUR_TOKEN>.
 * https://api.citysimulation.eu/<TEAM_KEY>/start
   * Method: Any
   * Description: You can start the simulation by using this API.
 * https://api.citysimulation.eu/<TEAM_KEY>/stop
   * Method: Any
   * Description: You can stop the simulation by using this API.
 * https://api.citysimulation.eu/<TEAM_KEY>/team
   * Method: Post
   * Description: You can create a team with field "team_name" and value <YOUR_TEAM_NAME> in a form in the POST request.

## Operation APIs
Operation APIs are used to check simulation information and operate cars. When a car is moved to the coordinate of a customer, it will automatically pick up the customer. When the car arrives at the destination of the customer, it will drop the customer automatically. Operation APIs require <TEAM_NAME> to access (given by the mentors). The <TEAM_NAME> can be shared with other teams.
* https://api.citysimulation.eu/<TEAM_NAME>/api/v1/world
  * Method: Any
  * <YOUR_TOKEN> Required for team specific information.
  * Description: You can get the information for the simulated world by using this API. Team specific information, such as picked customers, can be obtained with this API when you put the <YOUR_TOKEN> in your header.(e.g., Authorization: <YOUR_TOKEN>)
* https://api.citysimulation.eu/<TEAM_NAME>/api/v1/scores
  * Method: GET
  * Description: You can get the scores for all the teams on the server by using this API.
* https://api.citysimulation.eu/<TEAM_NAME>/api/v1/actions
  * Method: Post
  * <YOUR_TOKEN> Required
  * Description: You can operate your cars with a POST request similar to the following POST request with header "Authorization: <YOUR_TOKEN>". <car_id> can be obtained from the world API above. "MoveDirection" takes values from 0 to 3. 0 for North, 1 for East, 2 for South and 3 for West.
    * {
        "Type":"move",
        "Action":{
          "Message": "anything",
          "CarId": <car_id>,
          "MoveDirection": <[0-3]>
        }
      }
