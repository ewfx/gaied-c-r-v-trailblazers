public class CaseTriggerHandler {
    public static void handleAfterInsert(List<Case> newCases) {
        for (Case c : newCases) {
            // Prepare the payload
            Map<String, Object> payload = new Map<String, Object>();
            payload.put('caseId', c.Id);
            payload.put('subject', c.Subject);
            payload.put('description', c.Description);
            payload.put('status', c.Status);
            payload.put('UID__c', c.UID__c); // Include UID__c in the payload

            // Convert the payload to JSON
            String jsonPayload = JSON.serialize(payload);

            // Make the HTTP callout
            makeHttpCallout(jsonPayload);
        }
    }

    @future(callout=true)
    private static void makeHttpCallout(String jsonPayload) {
        try {
            Http http = new Http();
            HttpRequest request = new HttpRequest();
            request.setEndpoint('http://127.0.0.1:5000/api/data'); // Replace with your actual API endpoint
            request.setMethod('POST');
            request.setHeader('Content-Type', 'application/json');
            request.setBody(jsonPayload);

            HttpResponse response = http.send(request);

            // Log the response for debugging
            System.debug('Response Status: ' + response.getStatus());
            System.debug('Response Body: ' + response.getBody());
        } catch (Exception e) {
            System.debug('Error during HTTP callout: ' + e.getMessage());
        }
    }
}
