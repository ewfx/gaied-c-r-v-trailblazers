trigger CaseTrigger on Case (after insert) {
    // Call the helper class to process the inserted cases
    CaseTriggerHandler.handleAfterInsert(Trigger.new);
}
