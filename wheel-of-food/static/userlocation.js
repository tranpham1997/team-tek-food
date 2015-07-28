function getUserLocation(){
  //check if geolocation object is supported, if so get position
  if (navigator.geolocation)
    navigator.geolocation.getCurrentPosition(displayLocation, displayError);
  else {
    document.getElementById("locationData").innerHTML = "Sorry __ your browser doesn't support geolocation!";
  }
}
function displayLocation(position){
  //build text string including coordinate data passed in parameter
  //var displayText = "User latitude is " + position.coords.latitude + " longitude is " + position.coords.longitude;
  //display the string for demonstration
  //document.getElementById("locationData").innerHTML = displayText;
  //redirects to URL indicated below
  window.location = "../location?lat=" + position.coords.latitude + "&lon=" + position.coords.longitude;
  //var displayText = "User latitude is " + position.coords.latitude + " longitude is " + position.coords.longitude;
  //window.location = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + position.coords.latitude +','+position.coords.longitude + '&key=AIzaSyDIH9iVlHtpMY0BsBd3F3sn43Bmf4YV4mI';
  //display the string for demonstration
  //document.getElementById("locationData").innerHTML = displayText;
}
function returnLatitude(position){

  return position.coords.latitude;

}

function returnLongitude(position){

  return position.coords.latitude;

}
// function returnLatitude(position){
//
//   return position.coords.latitude;
//
// }
//
// function returnLongitude(position){
//
//   return position.coords.latitude;
//
// }
function displayError(error){
  //get a reference to the HTML element for writing result
  var locationElement = document.getElementById('locationData');

  //find out which error we have, output message accordingly
  switch(error.code){
    case error.PERMISSION_DENIED:
      locationElement.innerHTML ="Permission was denied";
      break;
    case error.POSITION_UNAVAILABLE:
      locationElement.innerHTML = "Location data not available";
      break;
    case error.UNKNOWN_ERROR:
      locationElement.innerHTML ="An unspecified error occurred";
      break;
    case error.TIMEOUT:
      locationElement.innerHTML = "Location request timeout";
      break;
    default:
      locationElement.innerHTML = "Who knows what happened...";
      break;
  }
}
