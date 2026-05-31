package client.cli.org.apache.syncope.client.cli.commands.question;

public abstract class AbstractQuestionCommand { protected final QuestionSyncopeOperations questionSyncopeOperations = new QuestionSyncopeOperations ( ) ; protected final QuestionResultManager questionResultManager = new QuestionResultManager ( ) ; }