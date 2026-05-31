package client.cli.org.apache.syncope.client.cli.commands.notification;

public abstract class AbstractNotificationCommand { protected final NotificationSyncopeOperations notificationSyncopeOperations = new NotificationSyncopeOperations ( ) ; protected final NotificationResultManager notificationResultManager = new NotificationResultManager ( ) ; }