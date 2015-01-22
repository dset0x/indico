# This file is part of Indico.
# Copyright (C) 2002 - 2015 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

import pytest

from indico.modules.payment.models.transactions import (PaymentTransaction, TransactionAction, TransactionStatus,
                                                        TransactionStatusTransition, IgnoredTransactionAction,
                                                        InvalidManualTransactionAction, InvalidTransactionAction,
                                                        DoublePaymentTransaction, InvalidTransactionStatus)


pytest_plugins = 'indico.modules.payment.testing.fixtures'


@pytest.fixture
def patch_transition_methods(mocker):
    mocker.patch.object(TransactionStatusTransition, '_next_from_initial')
    mocker.patch.object(TransactionStatusTransition, '_next_from_successful')
    mocker.patch.object(TransactionStatusTransition, '_next_from_pending')


@pytest.fixture
def creation_params(dummy_registrant):
    return {'registrant': dummy_registrant,
            'amount': 10,
            'currency': 'USD',
            'action': TransactionAction.complete,
            'provider': 'le-provider'}


# ======================================================================================================================
# TransactionStatusTransition tests
# ======================================================================================================================

@pytest.mark.usefixtures('patch_transition_methods')
@pytest.mark.parametrize(('status', 'expected_transition'), (
    (None,                         'initial'),
    (TransactionStatus.successful, 'successful'),
    (TransactionStatus.cancelled,  'initial'),
    (TransactionStatus.failed,     'initial'),
    (TransactionStatus.pending,    'pending'),
    (TransactionStatus.rejected,   'initial'),
))
def test_next(create_transaction, status, expected_transition):
    transaction = create_transaction(status) if status else None
    TransactionStatusTransition.next(transaction, TransactionAction.complete,  '_manual')
    if expected_transition == 'initial':
        assert TransactionStatusTransition._next_from_initial.called
    elif expected_transition == 'successful':
        assert TransactionStatusTransition._next_from_successful.called
    elif expected_transition == 'pending':
        assert TransactionStatusTransition._next_from_pending.called


@pytest.mark.usefixtures('patch_transition_methods')
@pytest.mark.parametrize(('provider', 'manual'), (
    ('_manual',   True),
    ('manual',    False),
    ('whatever',  False),
))
def test_next_providers(mocker, create_transaction, provider, manual):
    action = TransactionAction.complete
    initial_transaction = create_transaction(TransactionStatus.cancelled)
    successful_transaction = create_transaction(TransactionStatus.successful)
    pending_transaction = create_transaction(TransactionStatus.pending)
    # Test initial statuses
    TransactionStatusTransition.next(initial_transaction, action, provider)
    TransactionStatusTransition._next_from_initial.assert_called_with(action, manual)
    # Test successful statuses
    TransactionStatusTransition.next(successful_transaction, action, provider)
    TransactionStatusTransition._next_from_successful.assert_called_with(action, manual)
    # Test pending statuses
    TransactionStatusTransition.next(pending_transaction, action, provider)
    TransactionStatusTransition._next_from_pending.assert_called_with(action, manual)


def test_next_invalid(dummy_transaction):
    dummy_transaction.status = 'invalid status'
    with pytest.raises(InvalidTransactionStatus):
        TransactionStatusTransition.next(dummy_transaction, TransactionAction.complete, '')


@pytest.mark.parametrize(('action', 'manual', 'expected'), (
    (TransactionAction.complete, True,  TransactionStatus.successful),
    (TransactionAction.cancel,   True,  IgnoredTransactionAction),
    (TransactionAction.pending,  True,  InvalidManualTransactionAction),
    (TransactionAction.reject,   True,  InvalidManualTransactionAction),
    (TransactionAction.complete, False, TransactionStatus.successful),
    (TransactionAction.cancel,   False, InvalidTransactionAction),
    (TransactionAction.pending,  False, TransactionStatus.pending),
    (TransactionAction.reject,   False, IgnoredTransactionAction),
))
def test_next_from_initial(action, manual, expected):
    if isinstance(expected, TransactionStatus):
        assert TransactionStatusTransition._next_from_initial(action, manual) == expected
    else:
        with pytest.raises(expected):
            TransactionStatusTransition._next_from_initial(action, manual)


@pytest.mark.parametrize(('action', 'manual', 'expected'), (
    (TransactionAction.complete, True,  IgnoredTransactionAction),
    (TransactionAction.cancel,   True,  TransactionStatus.cancelled),
    (TransactionAction.pending,  True,  InvalidManualTransactionAction),
    (TransactionAction.reject,   True,  InvalidManualTransactionAction),
    (TransactionAction.complete, False, DoublePaymentTransaction),
    (TransactionAction.cancel,   False, InvalidTransactionAction),
    (TransactionAction.pending,  False, IgnoredTransactionAction),
    (TransactionAction.reject,   False, IgnoredTransactionAction),
))
def test_next_from_successful(action, manual, expected):
    if isinstance(expected, TransactionStatus):
        assert TransactionStatusTransition._next_from_successful(action, manual) == expected
    else:
        with pytest.raises(expected):
            TransactionStatusTransition._next_from_successful(action, manual)


@pytest.mark.parametrize(('action', 'manual', 'expected'), (
    (TransactionAction.complete, True,  IgnoredTransactionAction),
    (TransactionAction.cancel,   True,  TransactionStatus.cancelled),
    (TransactionAction.pending,  True,  InvalidManualTransactionAction),
    (TransactionAction.reject,   True,  InvalidManualTransactionAction),
    (TransactionAction.complete, False, TransactionStatus.successful),
    (TransactionAction.cancel,   False, InvalidTransactionAction),
    (TransactionAction.pending,  False, IgnoredTransactionAction),
    (TransactionAction.reject,   False, TransactionStatus.rejected),
))
def test_next_from_pending(action, manual, expected):
    if isinstance(expected, TransactionStatus):
        assert TransactionStatusTransition._next_from_pending(action, manual) == expected
    else:
        with pytest.raises(expected):
            TransactionStatusTransition._next_from_pending(action, manual)


# ======================================================================================================================
# PaymentTransaction tests
# ======================================================================================================================

def test_event(dummy_transaction, dummy_event):
    assert dummy_transaction.event == dummy_event


@pytest.mark.parametrize(('provider', 'expected'), (
    ('_manual', True),
    ('manual', False),
    ('le-provider', False),
))
def test_manual(dummy_transaction, provider, expected):
    dummy_transaction.provider = provider
    assert dummy_transaction.manual == expected


def test_create_next(creation_params):
    transaction, double_payment = PaymentTransaction.create_next(**creation_params)
    assert isinstance(transaction, PaymentTransaction)
    assert not double_payment


@pytest.mark.parametrize('exception', (
    InvalidTransactionStatus,
    InvalidManualTransactionAction,
    InvalidTransactionAction,
    IgnoredTransactionAction,
))
def test_create_next_with_exception(mock_get_logger, mocker, creation_params, exception):
    mocker.patch.object(TransactionStatusTransition, 'next')
    TransactionStatusTransition.next.side_effect = exception()
    transaction, double_payment = PaymentTransaction.create_next(**creation_params)
    assert transaction is None
    assert double_payment is None
    mock_get_logger.assert_called_once_with('payment')


def test_create_next_double_payment(mock_get_logger, create_transaction, creation_params):
    create_transaction(TransactionStatus.successful)
    _, double_payment = PaymentTransaction.create_next(**creation_params)
    mock_get_logger.assert_called_once_with('payment')
    assert double_payment


def test_find_latest_for_registrant(create_transaction, dummy_registrant):
    t1 = create_transaction(TransactionStatus.successful)
    t2 = create_transaction(TransactionStatus.successful)
    assert t1 != t2
    assert PaymentTransaction.find_latest_for_registrant(dummy_registrant) == t2